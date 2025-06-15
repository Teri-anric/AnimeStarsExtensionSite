from pydantic import BaseModel, Field
from typing import List, Optional
from .card import CardSchema
from .base import BaseSchema
from .pagination import BasePaginationResponse


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


class DeckQuery(BaseSchema):
    """Query parameters for deck searches"""
    query: Optional[str] = Field(None, description="Search query for anime name")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page") 