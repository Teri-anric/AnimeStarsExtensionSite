from .metadata_container import MetadataContainer
from .field_metadata import PropertyFieldMetadata
from ...database.models.animestars.card import Card


class DeckMetadataContainer(MetadataContainer):
    """Metadata container for Deck model"""

    def get_model_class(self) -> type:
        return Card

    def get_entity_code(self) -> str:
        return "deck"

    def __init__(self):
        super().__init__()
        
        self.add_field(PropertyFieldMetadata(Card.anime_link, "anime_link"))
        self.add_field(PropertyFieldMetadata(Card.anime_name, "anime_name"))
