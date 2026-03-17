from .crud import CRUDRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from .base import BaseRepository
from uuid import UUID
from typing import Iterable
from sqlalchemy import select, update
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

    async def partial_update_by_card_id_bulk(self, cards: Iterable[dict]) -> int:
        """
        Partially update existing cards by card_id.

        Only fields provided in each payload will be updated; other fields remain unchanged.
        Cards are not created if they do not already exist.
        """
        total = 0
        async with self.auto_commit() as session:
            for data in cards:
                card_id = data.get("card_id")
                if card_id is None:
                    continue
                fields = {k: v for k, v in data.items() if k != "card_id"}
                if not fields:
                    continue
                result = await session.execute(
                    update(Card).where(Card.card_id == card_id).values(**fields)
                )
                total += result.rowcount
        return total
