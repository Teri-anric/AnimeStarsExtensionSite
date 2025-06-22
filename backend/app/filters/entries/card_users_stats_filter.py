from uuid import UUID
from pydantic import Field
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import EnumFieldFilter, NumericFieldFilter
from ...database.enum import CardCollection


class CardUsersStatsFilter(BaseEntryFilter):

    id: EnumFieldFilter[UUID] | None = Field(default=None, description="Filter by ID")
    card_id: NumericFieldFilter | None = Field(default=None, description="Filter by Card ID")
    collection: EnumFieldFilter[CardCollection] | None = Field(default=None, description="Filter by Collection type")
    count: NumericFieldFilter | None = Field(default=None, description="Filter by Count")
    
    @classmethod
    def get_entry_code(cls) -> str:
        return  "card_users_stats"
