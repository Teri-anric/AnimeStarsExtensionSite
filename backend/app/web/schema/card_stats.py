from datetime import datetime
from .base import BaseSchema
from typing import Literal
from ...filters.entries.card_users_stats_filter import CardUsersStatsFilter
from ...database.enum import CardCollection
from .pagination import BasePaginationQuery, BasePaginationResponse
from uuid import UUID

class CardUsersStatsSchema(BaseSchema):
    id: UUID
    card_id: int
    collection: CardCollection
    count: int
    created_at: datetime
    updated_at: datetime



CardUsersStatsSort = Literal["id", "card_id", "collection", "count", "created_at", "updated_at"] 

class CardUsersStatsQuery(BasePaginationQuery[CardUsersStatsFilter, CardUsersStatsSort]):
    pass

class CardUsersStatsResponse(BasePaginationResponse[CardUsersStatsSchema]):
    items: list[CardUsersStatsSchema]