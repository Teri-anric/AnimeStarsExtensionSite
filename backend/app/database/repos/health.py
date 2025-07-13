from datetime import datetime
from sqlalchemy import select, func
from .base import BaseRepository
from ..models.animestars.card import Card
from ..models.user import User
from ..models.animestars.card_users_stats import CardUsersStats


class HealthRepository(BaseRepository):
    async def get_total_cards_count(self) -> int:
        return await self.scalar(select(func.count(Card.id)))

    async def get_total_users_count(self) -> int:
        return await self.scalar(select(func.count(User.id)))

    async def get_total_cards_with_stats_count(self) -> int:
        return await self.scalar(
            select(func.count(Card.id)).where(Card.stats_count > 0)
        )

    async def get_total_cards_stats_count(self) -> int:
        return await self.scalar(select(func.count(CardUsersStats.id)))

    async def get_total_cards_stats_today_count(self) -> int:
        return await self.scalar(
            select(func.count(CardUsersStats.id)).where(
                func.date(CardUsersStats.created_at) == datetime.now().date()
            )
        )
