from .crud import CRUDRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from ..models.animestars.summary_card_users import SummaryCardUsers
from .base import BaseRepository
from sqlalchemy import select, or_
from ..enum import CardCollection
from uuid import UUID
from sqlalchemy.sql.expression import Select
from ..types.filter import RawFilter


class CardRepository(
    CRUDRepository[Card, UUID], PaginationRepository[Card], BaseRepository
):
    @property
    def entry_class(self) -> type[Card]:
        return Card
    
    async def get_by_card_id(self, card_id: int) -> Card | None:
        return await self.get_one_by(RawFilter(statement=Card.card_id.__eq__(card_id)))
    
    async def get_by_ident(self, ident: int | UUID) -> Card | None:
        if isinstance(ident, int):
            return await self.get_by_card_id(ident)
        return await self.get(ident)
