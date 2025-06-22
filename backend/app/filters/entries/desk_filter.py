
from pydantic import Field
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import StringFieldFilter


class DeckFilter(BaseEntryFilter):
    """Entry filter for Deck model - pure data model"""
    
    # Field filters
    anime_name: StringFieldFilter | None = Field(default=None, description="Filter by Anime Name of the deck")
    anime_link: StringFieldFilter | None = Field(default=None, description="Filter by Anime Link of the deck")
    
    @classmethod
    def get_entry_code(cls) -> str:
        return "deck"
