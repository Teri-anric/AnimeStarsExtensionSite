from uuid import UUID
from sqlalchemy import select, func
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from .crud import CRUDRepository
from .pagination import PaginationRepository

class CardUsersStatsRepository(
    CRUDRepository[CardUsersStats, UUID],
    PaginationRepository[CardUsersStats],
    BaseRepository,
):
    @property
    def entry_class(self) -> type[CardUsersStats]:
        return CardUsersStats
    
    @property
    def entry_code(self) -> str:
        return "card_users_stats"

    async def get_last_card_users_stats(
        self, card_id: int
    ) -> list[CardUsersStats]:        
        results = await self.scalars(
            select(
                CardUsersStats
            )
            .where(
                CardUsersStats.card_id == card_id
            )
            .order_by(CardUsersStats.collection, CardUsersStats.created_at.desc())
            .distinct(CardUsersStats.collection)
        )
        return results

    async def get_last_card_users_stats_bulk(
        self, card_ids: list[int]
    ) -> list[CardUsersStats]:
        results = await self.scalars(
            select(CardUsersStats)
            .where(CardUsersStats.card_id.in_(card_ids))
            .order_by(CardUsersStats.card_id, CardUsersStats.collection, CardUsersStats.created_at.desc())
            .distinct(CardUsersStats.card_id, CardUsersStats.collection)
        )
        return results
