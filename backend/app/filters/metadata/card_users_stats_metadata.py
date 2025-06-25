from .metadata_container import MetadataContainer
from .field_metadata import PropertyFieldMetadata
from ...database.models.animestars.card_users_stats import CardUsersStats


class CardUsersStatsMetadataContainer(MetadataContainer):
    """Metadata container for CardUsersStats model"""

    def get_model_class(self) -> type:
        return CardUsersStats

    def get_entity_code(self) -> str:
        return "card_users_stats"

    def __init__(self):
        super().__init__()
        
        self.add_field(PropertyFieldMetadata(CardUsersStats.id, "id"))
        self.add_field(PropertyFieldMetadata(CardUsersStats.card_id, "card_id"))
        self.add_field(PropertyFieldMetadata(CardUsersStats.collection, "collection"))
        self.add_field(PropertyFieldMetadata(CardUsersStats.count, "count"))
        self.add_field(PropertyFieldMetadata(CardUsersStats.created_at, "created_at"))
        self.add_field(PropertyFieldMetadata(CardUsersStats.updated_at, "updated_at"))
