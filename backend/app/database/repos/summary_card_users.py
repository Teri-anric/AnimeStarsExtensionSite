from ..models.animestars.summary_card_users import SummaryCardUsers
from .base import BaseRepository
from .crud import CRUDRepository
from uuid import UUID
from .pagination import PaginationRepository
from sqlalchemy import select
from ..enum import CardCollection
from ..types.filter import FilterProperty


class SummaryCardUsersRepository(
    CRUDRepository[SummaryCardUsers, UUID],
    PaginationRepository[SummaryCardUsers],
    BaseRepository,
):
    entry_code = "summary_card_users"

    @property
    def entry_class(self) -> type[SummaryCardUsers]:
        return SummaryCardUsers

    def _get_card_id_filter(self, card_id: int | UUID):
        if isinstance(card_id, int):
            return FilterProperty("card_id", card_id)
        return FilterProperty("id", card_id)

    async def get_card_users_summary(
        self, card_id: int | UUID
    ) -> dict[CardCollection, SummaryCardUsers]:
        results = await self.get_by(self._get_card_id_filter(card_id))
        return {item.collection: item for item in results}

    async def get_card_users_summary_by_collection(
        self, card_id: int, collection: CardCollection
    ) -> SummaryCardUsers:
        result = await self.get_one_by(
            FilterProperty("card_id", card_id)
            & FilterProperty("collection", collection)
        )
        return result
