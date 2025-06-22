from .crud import CRUDRepository
from .pagination import PaginationRepository
from ..models.animestars.card import Card
from .base import BaseRepository
from uuid import UUID


class CardRepository(
    CRUDRepository[Card, UUID], PaginationRepository[Card], BaseRepository
):    
    @property
    def entry_class(self) -> type[Card]:
        return Card
    
    async def get_by_card_id(self, card_id: int) -> Card | None:
        return await self.get_one_by(dict(card_id=card_id))
    
    async def get_by_ident(self, ident: int | UUID) -> Card | None:
        if isinstance(ident, int):
            return await self.get_by_card_id(ident)
        return await self.get(ident)
