from uuid import UUID
from pydantic import Field
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import StringFieldFilter, EnumFieldFilter, DateTimeFieldFilter
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
    created_at: DateTimeFieldFilter | None = Field(default=None, description="Filter by Creation date of the card")
    updated_at: DateTimeFieldFilter | None = Field(default=None, description="Filter by Last update date of the card")

    @classmethod
    def get_entry_code(cls) -> str:
        return "card" 