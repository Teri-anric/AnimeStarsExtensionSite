from uuid import UUID

from pydantic import Field
from typing import List, Literal
from .card import CardSchema, CardFilter
from .base import BaseSchema
from .pagination import BasePaginationResponse, BasePaginationQuery
from app.filters.types import ArrayEntryFilter, StringFilter, IntFilter, BaseFilter, UUIDEntryFilter


class DeckSummarySchema(BaseSchema):
    """Schema for deck summary in listings"""

    id: UUID
    anime_name: str
    anime_link: str | None = None
    card_count: int
    cards: List[CardSchema] = Field(default_factory=list)


class DeckPaginationResponse(BasePaginationResponse[DeckSummarySchema]):
    """Paginated response for deck listings"""

    items: List[DeckSummarySchema]


class DeckDetailSchema(BaseSchema):
    """Schema for detailed deck view with all cards"""

    id: UUID
    anime_name: str
    anime_link: str | None = None
    cards: List[CardSchema]


DeckSort = Literal[
    "id",
    "anime_name",
    "anime_link",
    "card_count",
]


class DeckFilter(BaseFilter):
    cards: ArrayEntryFilter[CardFilter] | None = None
    id: UUIDEntryFilter | None = None
    anime_name: StringFilter | None = None
    anime_link: StringFilter | None = None
    card_count: IntFilter | None = None


class DeckQuery(BasePaginationQuery[DeckFilter, DeckSort | str]):
    pass
