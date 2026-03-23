import uuid
from typing import Any

from sqlalchemy import func, select, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..deck_key import canonical_deck_key
from .pagination import PaginationRepository
from ..models.animestars.deck import AnimestarsDeck
from ..types.pagination import PaginationQuery, Pagination


class DeckRepository(PaginationRepository[AnimestarsDeck]):
    """Repository for animestars decks (unique canonical anime_name)."""

    @property
    def entry_class(self) -> type[AnimestarsDeck]:  # type: ignore
        return AnimestarsDeck

    @staticmethod
    async def ensure_deck_id(
        session: AsyncSession,
        anime_link: str | None,
        anime_name: str | None,
    ) -> uuid.UUID | None:
        key = canonical_deck_key(anime_name, anime_link)
        if not key:
            return None
        insert_stmt = pg_insert(AnimestarsDeck).values(
            id=uuid.uuid4(),
            anime_name=key,
            anime_link=anime_link,
            created_at=func.now(),
            updated_at=func.now(),
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[AnimestarsDeck.anime_name],
            set_={
                "anime_link": func.coalesce(
                    insert_stmt.excluded.anime_link,
                    AnimestarsDeck.anime_link,
                ),
                "updated_at": func.now(),
            },
        ).returning(AnimestarsDeck.id)
        result = await session.execute(insert_stmt)
        return result.scalar_one()

    @staticmethod
    async def attach_deck_ids(session: AsyncSession, values: list[dict[str, Any]]) -> None:
        """Mutates each card dict: sets deck_id from canonical deck key (name or link)."""
        by_key: dict[str, str | None] = {}
        for v in values:
            key = canonical_deck_key(v.get("anime_name"), v.get("anime_link"))
            if key:
                by_key[key] = v.get("anime_link")

        if not by_key:
            for v in values:
                v["deck_id"] = None
            return

        rows = [
            {
                "id": uuid.uuid4(),
                "anime_name": key,
                "anime_link": link,
                "created_at": func.now(),
                "updated_at": func.now(),
            }
            for key, link in by_key.items()
        ]
        insert_stmt = pg_insert(AnimestarsDeck).values(rows)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[AnimestarsDeck.anime_name],
            set_={
                "anime_link": func.coalesce(
                    insert_stmt.excluded.anime_link,
                    AnimestarsDeck.anime_link,
                ),
                "updated_at": func.now(),
            },
        ).returning(AnimestarsDeck.id, AnimestarsDeck.anime_name)
        result = await session.execute(insert_stmt)
        mapping = {r.anime_name: r.id for r in result.all()}

        for v in values:
            key = canonical_deck_key(v.get("anime_name"), v.get("anime_link"))
            v["deck_id"] = mapping.get(key) if key else None

    async def search(self, query: PaginationQuery) -> Pagination[AnimestarsDeck]:
        return await self.paginate(
            select(AnimestarsDeck).options(selectinload(AnimestarsDeck.cards)),
            query,
        )

    async def get_deck_by_id(self, deck_id: uuid.UUID) -> AnimestarsDeck | None:
        return await self.scalar(
            select(AnimestarsDeck)
            .where(AnimestarsDeck.id == deck_id)
            .options(selectinload(AnimestarsDeck.cards))
        )

    async def delete_empty_decks(self) -> int:
        return await self.execute(
            delete(AnimestarsDeck).where(AnimestarsDeck.card_count == 0)
        )