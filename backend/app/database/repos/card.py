from .crud import CRUDRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from .base import BaseRepository
from uuid import UUID
from typing import Iterable
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


class CardRepository(
    CRUDRepository[Card, UUID], PaginationRepository[Card], BaseRepository
):
    @property
    def entry_class(self) -> type[Card]:
        return Card

    async def get_by_card_id(self, card_id: int) -> Card | None:
        return await self.scalar(select(Card).where(Card.card_id == card_id))

    async def get_by_ident(self, ident: int | UUID) -> Card | None:
        if isinstance(ident, int):
            return await self.get_by_card_id(ident)
        return await self.get(ident)

    async def upsert_bulk(self, cards: Iterable[dict]) -> int:
        values = list(cards)
        if not values:
            return 0
        stmt = insert(Card).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["card_id"],
            set_={
                "name": stmt.excluded.name,
                "rank": stmt.excluded.rank,
                "anime_name": stmt.excluded.anime_name,
                "anime_link": stmt.excluded.anime_link,
                "author": stmt.excluded.author,
                "image": stmt.excluded.image,
                "mp4": stmt.excluded.mp4,
                "webm": stmt.excluded.webm,
            },
        )
        async with self.auto_commit() as session:
            result = await session.execute(stmt)
        return result.rowcount
