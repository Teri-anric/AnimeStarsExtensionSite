import uuid
from typing import Any

from sqlalchemy import func, select, delete, exists, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..deck_key import canonical_deck_key, anime_id_from_link
from .pagination import PaginationRepository
from ..models.animestars.deck import AnimestarsDeck
from ..models.animestars.card import Card
from ..types.pagination import PaginationQuery, Pagination


class DeckRepository(PaginationRepository[AnimestarsDeck]):
    """Repository for animestars decks, identified by the stable anime ID."""

    @property
    def entry_class(self) -> type[AnimestarsDeck]:  # type: ignore
        return AnimestarsDeck

    @staticmethod
    async def ensure_deck_id(
        session: AsyncSession,
        anime_link: str | None,
        anime_name: str | None,
        anime_id: int | None = None,
    ) -> uuid.UUID | None:
        key = canonical_deck_key(anime_name, anime_link)
        anime_id = anime_id or anime_id_from_link(anime_link)
        if not key or not anime_id:
            return None
        existing_id = await session.scalar(
            select(AnimestarsDeck.id).where(AnimestarsDeck.anime_id == anime_id)
        )
        if existing_id:
            await session.execute(
                update(AnimestarsDeck)
                .where(AnimestarsDeck.id == existing_id)
                .values(
                    anime_link=func.coalesce(anime_link, AnimestarsDeck.anime_link),
                    updated_at=func.now(),
                )
            )
            return existing_id
        insert_stmt = pg_insert(AnimestarsDeck).values(
            id=uuid.uuid4(),
            anime_name=key,
            anime_link=anime_link,
            anime_id=anime_id,
            created_at=func.now(),
            updated_at=func.now(),
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[AnimestarsDeck.anime_id],
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
        """Mutates each card dict: sets deck_id from the stable anime ID in its link."""
        by_anime_id: dict[int, tuple[str, str | None]] = {}
        for v in values:
            if v.get("deck_id"):
                continue
            key = canonical_deck_key(v.get("anime_name"), v.get("anime_link"))
            anime_id = anime_id_from_link(v.get("anime_link"))
            if key and anime_id:
                by_anime_id[anime_id] = (key, v.get("anime_link"))

        if not by_anime_id:
            for v in values:
                if not v.get("deck_id"):
                    v["deck_id"] = None
            return

        rows = [
            {
                "id": uuid.uuid4(),
                "anime_name": key,
                "anime_link": link,
                "anime_id": anime_id,
                "created_at": func.now(),
                "updated_at": func.now(),
            }
            for anime_id, (key, link) in by_anime_id.items()
        ]
        insert_stmt = pg_insert(AnimestarsDeck).values(rows)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[AnimestarsDeck.anime_id],
            set_={
                "anime_link": func.coalesce(
                    insert_stmt.excluded.anime_link,
                    AnimestarsDeck.anime_link,
                ),
                "updated_at": func.now(),
            },
            where=AnimestarsDeck.anime_link.is_distinct_from(insert_stmt.excluded.anime_link),
        ).returning(AnimestarsDeck.id, AnimestarsDeck.anime_id)
        result = await session.execute(insert_stmt)
        mapping = {r.anime_id: r.id for r in result.all()}

        # PostgreSQL RETURNING omits rows skipped by the no-op WHERE clause.
        # Resolve them in one read instead of rewriting their deck rows.
        missing_anime_ids = set(by_anime_id) - set(mapping)
        if missing_anime_ids:
            existing = await session.execute(
                select(AnimestarsDeck.id, AnimestarsDeck.anime_id).where(
                    AnimestarsDeck.anime_id.in_(missing_anime_ids)
                )
            )
            mapping.update({row.anime_id: row.id for row in existing.all()})

        for v in values:
            if v.get("deck_id"):
                continue
            anime_id = anime_id_from_link(v.get("anime_link"))
            v["deck_id"] = mapping.get(anime_id) if anime_id else None

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
            delete(AnimestarsDeck).where(
                ~exists(select(Card.id).where(Card.deck_id == AnimestarsDeck.id))
            )
        )
