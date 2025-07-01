from pydantic import Field
from typing import List, Literal
from .card import CardSchema
from .base import BaseSchema
from .pagination import BasePaginationResponse, BasePaginationQuery

class DeckSummarySchema(BaseSchema):
    """Schema for deck summary in listings"""
    anime_link: str
    anime_name: str | None
    card_count: int
    preview_cards: List[CardSchema] = Field(default_factory=list, description="First 6 cards for preview")


class DeckPaginationResponse(BasePaginationResponse[DeckSummarySchema]):
    """Paginated response for deck listings"""
    items: List[DeckSummarySchema]


class DeckDetailSchema(BaseSchema):
    """Schema for detailed deck view with all cards"""
    anime_link: str
    anime_name: str | None
    cards: List[CardSchema]


DeckSort = Literal[
    "anime_name asc",
    "anime_name desc", 
    "anime_name",
    "card_count asc",
    "card_count desc",
    "card_count",
]


class DeckQuery(BasePaginationQuery[dict, DeckSort]):
    pass