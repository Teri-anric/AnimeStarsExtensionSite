from pydantic import Field, BaseModel
from typing import List, Literal
from .card import CardSchema
from .base import BaseSchema
from .pagination import BasePaginationResponse, BasePaginationQuery
from app.filters.types import ArrayEntryFilter, StringFilter, IntFilter, BaseFilter


class DeckSummarySchema(BaseSchema):
    """Schema for deck summary in listings"""

    anime_link: str
    anime_name: str | None
    card_count: int
    cards: List[CardSchema] = Field(default_factory=list)


class DeckPaginationResponse(BasePaginationResponse[DeckSummarySchema]):
    """Paginated response for deck listings"""

    items: List[DeckSummarySchema]


class DeckDetailSchema(BaseSchema):
    """Schema for detailed deck view with all cards"""

    anime_link: str
    anime_name: str | None
    cards: List[CardSchema]


DeckSort = Literal[
    "anime_name",
    "anime_link",
    "card_count",
]


class DeckFilter(BaseFilter):
    cards: ArrayEntryFilter[CardSchema] | None = None
    anime_name: StringFilter | None = None
    anime_link: StringFilter | None = None
    card_count: IntFilter | None = None


class DeckQuery(BasePaginationQuery[DeckFilter, DeckSort | str]):
    pass
