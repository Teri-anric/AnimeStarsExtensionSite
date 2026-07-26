from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert

from app.database.models.extension_labyrinth_room import ExtensionLabyrinthRoom
from app.database.models.extension_labyrinth_room_history import ExtensionLabyrinthRoomHistory

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

    async def history(self, *, x: int, y: int, limit: int = 50) -> list[ExtensionLabyrinthRoomHistory]:
        stmt = (
            select(ExtensionLabyrinthRoomHistory)
            .join(ExtensionLabyrinthRoom, ExtensionLabyrinthRoom.id == ExtensionLabyrinthRoomHistory.room_id)
            .where(ExtensionLabyrinthRoom.x == x, ExtensionLabyrinthRoom.y == y)
            .order_by(ExtensionLabyrinthRoomHistory.created_at.desc())
            .limit(limit)
        )
        return await self.scalars(stmt)

    async def bulk_upsert(self, rooms: list[dict]) -> int:
        deduped: dict[tuple[int, int], dict] = {}
        for room in rooms:
            deduped[(room["x"], room["y"])] = room
        if not deduped:
            return 0

        coordinates = list(deduped)
        async with self.session as session:
            existing_rooms = (
                await session.execute(
                    select(ExtensionLabyrinthRoom).where(
                        tuple_(ExtensionLabyrinthRoom.x, ExtensionLabyrinthRoom.y).in_(coordinates)
                    )
                )
            ).scalars().all()
            existing_by_coordinates = {(room.x, room.y): room for room in existing_rooms}

            now = func.now()
            rows = [
                {
                    "x": room["x"],
                    "y": room["y"],
                    "event": room.get("event"),
                    "sources_count": 1,
                    "emission_event": room.get("emission_event"),
                    "emission_sources_count": 1 if room.get("emission_event") else 0,
                    "emission_observed_at": now if room.get("emission_event") else None,
                }
                for room in deduped.values()
            ]
            stmt = insert(ExtensionLabyrinthRoom).values(rows)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_extension_labyrinth_rooms_xy",
                set_={
                    # Never let an unknown observation erase a known room type.
                    # Emission-only rows have event=NULL and therefore leave it intact.
                    "event": case(
                        (
                            (stmt.excluded.event.is_(None))
                            | (stmt.excluded.event == "unknown"),
                            ExtensionLabyrinthRoom.event,
                        ),
                        else_=stmt.excluded.event,
                    ),
                    "sources_count": case(
                        (stmt.excluded.event.is_not(None), ExtensionLabyrinthRoom.sources_count + 1),
                        else_=ExtensionLabyrinthRoom.sources_count,
                    ),
                    "emission_event": case(
                        (stmt.excluded.emission_event.is_not(None), stmt.excluded.emission_event),
                        else_=ExtensionLabyrinthRoom.emission_event,
                    ),
                    "emission_sources_count": case(
                        (
                            stmt.excluded.emission_event.is_not(None),
                            ExtensionLabyrinthRoom.emission_sources_count + 1,
                        ),
                        else_=ExtensionLabyrinthRoom.emission_sources_count,
                    ),
                    "emission_observed_at": case(
                        (stmt.excluded.emission_event.is_not(None), now),
                        else_=ExtensionLabyrinthRoom.emission_observed_at,
                    ),
                    "updated_at": now,
                },
            )
            await session.execute(stmt)

            rooms_after_upsert = (
                await session.execute(
                    select(ExtensionLabyrinthRoom).where(
                        tuple_(ExtensionLabyrinthRoom.x, ExtensionLabyrinthRoom.y).in_(coordinates)
                    )
                )
            ).scalars().all()
            rooms_after_by_coordinates = {(room.x, room.y): room for room in rooms_after_upsert}
            history_rows: list[ExtensionLabyrinthRoomHistory] = []
            for coordinates, incoming in deduped.items():
                previous = existing_by_coordinates.get(coordinates)
                current = rooms_after_by_coordinates[coordinates]
                event = incoming.get("event")
                if event and event != "unknown" and (previous is None or previous.event != event):
                    history_rows.append(ExtensionLabyrinthRoomHistory(room_id=current.id, event=event))
                emission_event = incoming.get("emission_event")
                if emission_event and (previous is None or previous.emission_event != emission_event):
                    history_rows.append(
                        ExtensionLabyrinthRoomHistory(room_id=current.id, event=emission_event, is_emission=True)
                    )
            session.add_all(history_rows)
            await session.commit()
        return len(rows)
