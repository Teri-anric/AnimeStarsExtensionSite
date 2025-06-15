from dataclasses import dataclass
from typing import List
from uuid import UUID
from datetime import datetime

from ..models.animestars.card import Card, CardType


@dataclass
class DeckSummaryDTO:
    """DTO for deck summary in listings"""
    anime_link: str
    anime_name: str | None
    card_count: int
    preview_cards: List[Card]


@dataclass
class DeckPaginationDTO:
    """DTO for paginated deck response"""
    items: List[DeckSummaryDTO]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool


@dataclass
class DeckDetailDTO:
    """DTO for detailed deck view with all cards"""
    anime_link: str
    anime_name: str | None
    cards: List[Card] 