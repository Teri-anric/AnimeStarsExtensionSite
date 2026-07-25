from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.database.models.extension_labyrinth_room import ExtensionLabyrinthRoom

from .base import BaseRepository


class ExtensionLabyrinthRoomRepository(BaseRepository):
    async def list_map(
        self,
        *,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
        updated_after: datetime | None = None,
    ) -> list[ExtensionLabyrinthRoom]:
        stmt = (
            select(ExtensionLabyrinthRoom)
            .where(
                ExtensionLabyrinthRoom.x >= min_x,
                ExtensionLabyrinthRoom.x <= max_x,
                ExtensionLabyrinthRoom.y >= min_y,
                ExtensionLabyrinthRoom.y <= max_y,
            )
            .order_by(ExtensionLabyrinthRoom.x, ExtensionLabyrinthRoom.y)
        )
        if updated_after is not None:
            stmt = stmt.where(ExtensionLabyrinthRoom.updated_at > updated_after)
        return await self.scalars(stmt)

    async def summary(self) -> dict:
        async with self.session as session:
            bounds_result = await session.execute(
                select(
                    func.count(ExtensionLabyrinthRoom.id),
                    func.min(ExtensionLabyrinthRoom.x),
                    func.max(ExtensionLabyrinthRoom.x),
                    func.min(ExtensionLabyrinthRoom.y),
                    func.max(ExtensionLabyrinthRoom.y),
                    func.max(ExtensionLabyrinthRoom.updated_at),
                )
            )
            total, min_x, max_x, min_y, max_y, updated_at = bounds_result.one()

            events_result = await session.execute(
                select(ExtensionLabyrinthRoom.event, func.count(ExtensionLabyrinthRoom.id))
                .group_by(ExtensionLabyrinthRoom.event)
                .order_by(ExtensionLabyrinthRoom.event)
            )
            events = {
                (event or "unknown"): count
                for event, count in events_result.all()
            }

            return {
                "total_rooms": total,
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
                "updated_at": updated_at,
                "events": events,
            }

    async def bulk_upsert(self, rooms: list[dict]) -> int:
        deduped: dict[tuple[int, int], dict] = {}
        for room in rooms:
            deduped[(room["x"], room["y"])] = room
        if not deduped:
            return 0

        now = func.now()
        rows = [
            {
                "x": room["x"],
                "y": room["y"],
                "event": room.get("event"),
                "sources_count": 1,
            }
            for room in deduped.values()
        ]
        stmt = insert(ExtensionLabyrinthRoom).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_extension_labyrinth_rooms_xy",
            set_={
                "event": stmt.excluded.event,
                "sources_count": ExtensionLabyrinthRoom.sources_count + 1,
                "updated_at": now,
            },
        )

        async with self.session as session:
            await session.execute(stmt)
            await session.commit()
        return len(rows)
