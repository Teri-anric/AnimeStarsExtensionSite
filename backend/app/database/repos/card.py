from .crud import CRUDRepository
from ..models.animestars.card import Card


class CardRepository(CRUDRepository[Card]):
    @property
    def entry_class(self) -> type[Card]:
        return Card

