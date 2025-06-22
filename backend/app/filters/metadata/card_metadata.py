from .metadata_container import MetadataContainer
from .field_metadata import PropertyFieldMetadata
from ...database.models.animestars.card import Card


class CardMetadataContainer(MetadataContainer):
    """Metadata container for Card model"""

    def get_model_class(self) -> type:
        return Card

    def get_entity_code(self) -> str:
        return "card"

    def __init__(self):
        super().__init__()
        
        self.add_field(PropertyFieldMetadata(Card.id, "id"))
        self.add_field(PropertyFieldMetadata(Card.card_id, "card_id"))
        self.add_field(PropertyFieldMetadata(Card.name, "name"))
        self.add_field(PropertyFieldMetadata(Card.rank, "rank"))
        self.add_field(PropertyFieldMetadata(Card.anime_name, "anime_name"))
        self.add_field(PropertyFieldMetadata(Card.anime_link, "anime_link"))
        self.add_field(PropertyFieldMetadata(Card.author, "author"))
        self.add_field(PropertyFieldMetadata(Card.image, "image"))
        self.add_field(PropertyFieldMetadata(Card.mp4, "mp4"))
        self.add_field(PropertyFieldMetadata(Card.webm, "webm"))
