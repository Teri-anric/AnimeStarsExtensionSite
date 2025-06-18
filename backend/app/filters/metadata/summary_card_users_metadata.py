from sqlalchemy import Select
from .metadata_container import MetadataContainer
from .field_metadata import PropertyFieldMetadata
from ...database.models.animestars.summary_card_users import SummaryCardUsers


class SummaryCardUsersMetadataContainer(MetadataContainer):
    """Metadata container for SummaryCardUsers model"""

    def get_model_class(self) -> type:
        return SummaryCardUsers

    def get_entity_code(self) -> str:
        return "summary_card_users"
    
    def __init__(self):
        super().__init__()

        # Regular field properties
        self.add_field(PropertyFieldMetadata(SummaryCardUsers.id, "id"))
        self.add_field(PropertyFieldMetadata(SummaryCardUsers.card_id, "card_id"))
        self.add_field(PropertyFieldMetadata(SummaryCardUsers.collection, "collection"))
        self.add_field(PropertyFieldMetadata(SummaryCardUsers.state, "state"))
        self.add_field(PropertyFieldMetadata(SummaryCardUsers.count, "count"))
