from sqlalchemy import Select, and_, aliased
from .metadata_container import MetadataContainer
from .field_metadata import PropertyFieldMetadata, BaseJoinHandler
from ..models.field_filters import ArrayFieldFilter
from ...database.models.animestars.card import Card
from ...database.models.animestars.summary_card_users import SummaryCardUsers


class SummaryCardUsersJoinHandler(BaseJoinHandler):
    """Join handler for SummaryCardUsers"""

    def __init__(self):
        self._alias = aliased(SummaryCardUsers)

    @property
    def alias(self):
        return self._alias

    def prepare_query(self, stmt: Select, parent_alias=None) -> Select:
        """Prepare query by adding necessary JOINs with parent alias context"""
        return stmt.join(self.alias, self.alias.card_id == (parent_alias or Card).card_id)


class CardMetadataContainer(MetadataContainer):
    """Metadata container for Card model"""

    def __init__(self):
        super().__init__()
        
        # Regular field properties
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

    def get_model_class(self) -> type:
        return Card

    def get_entity_code(self) -> str:
        return "card"
    
    def get_join(self, property_code: str) -> BaseJoinHandler | None:
        """Get join handler for property code - implement in subclasses"""
        if property_code == "summary_card_users":
            return SummaryCardUsersJoinHandler()
        return None
