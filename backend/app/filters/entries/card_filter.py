from uuid import UUID
from pydantic import Field
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import StringFieldFilter, EnumFieldFilter
from .summary_card_users_filter import SummaryCardUsersFilter
from ...database.enum import CardType


class CardFilter(BaseEntryFilter):
    """Entry filter for Card model - pure data model"""
    
    # Field filters
    id: EnumFieldFilter[UUID] | None = Field(default=None, description="Filter by ID of the card")
    card_id: EnumFieldFilter[int] | None = Field(default=None, description="Filter by Card ID of the card")
    name: StringFieldFilter | None = Field(default=None, description="Filter by Name of the card")
    rank: EnumFieldFilter[CardType] | None = Field(default=None, description="Filter by Rank of the card")
    anime_name: StringFieldFilter | None = Field(default=None, description="Filter by Anime Name of the card")
    anime_link: StringFieldFilter | None = Field(default=None, description="Filter by Anime Link of the card")
    author: StringFieldFilter | None = Field(default=None, description="Filter by Author of the card")
    image: StringFieldFilter | None = Field(default=None, description="Filter by Image of the card")
    mp4: StringFieldFilter | None = Field(default=None, description="Filter by MP4 of the card")
    webm: StringFieldFilter | None = Field(default=None, description="Filter by WebM of the card")
    
    # Entry filter for join filtering
    summary_card_users: SummaryCardUsersFilter | None = Field(
        default=None, 
        description="Filter cards by their related SummaryCardUsers records"
    )
    
    @classmethod
    def get_entry_code(cls) -> str:
        return "card" 