from pydantic import Field
from ..models.entry_filters import BaseEntryFilter
from ..models.field_filters import StringFieldFilter, EnumFieldFilter, NumericFieldFilter
from ...database.enum import CardCollection, SummaryCardState


class SummaryCardUsersFilter(BaseEntryFilter):
    """Entry filter for SummaryCardUsers model - used as submodel filter in ArrayFieldFilter"""
    
    entry_code = "summary_card_users"
    
    # Field filters for SummaryCardUsers model
    card_id: NumericFieldFilter | None = Field(default=None, description="Filter by Card ID")
    collection: EnumFieldFilter[CardCollection] | None = Field(default=None, description="Filter by Collection type")
    state: EnumFieldFilter[SummaryCardState] | None = Field(default=None, description="Filter by State")
    count: NumericFieldFilter | None = Field(default=None, description="Filter by Count")
    
    @classmethod
    def get_entry_code(cls) -> str:
        return cls.entry_code 