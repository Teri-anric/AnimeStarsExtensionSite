from datetime import datetime
from .base import BaseSchema
from typing import Literal
from ...database.enum import CardCollection
from .pagination import BasePaginationQuery, BasePaginationResponse
from uuid import UUID
from ...filters import BaseFilter, UUIDEntryFilter, IntegerEntryFilter, EnumEntryFilter, DateTimeEntryFilter

class CardUsersStatsSchema(BaseSchema):
    id: UUID
    card_id: int
    collection: CardCollection
    count: int
    created_at: datetime
    updated_at: datetime



CardUsersStatsSort = Literal["id", "card_id", "collection", "count", "created_at", "updated_at"] 

class CardUsersStatsFilter(BaseFilter):
    """Filter schema for CardUsersStats model"""
    id: UUIDEntryFilter | None = None
    card_id: IntegerEntryFilter | None = None
    collection: EnumEntryFilter[CardCollection] | None = None
    count: IntegerEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None


class CardUsersStatsQuery(BasePaginationQuery[CardUsersStatsFilter, CardUsersStatsSort]):
    pass

class CardUsersStatsResponse(BasePaginationResponse[CardUsersStatsSchema]):
    items: list[CardUsersStatsSchema]
