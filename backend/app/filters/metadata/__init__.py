from .card_metadata import CardMetadataContainer
from .summary_card_users_metadata import SummaryCardUsersMetadataContainer
from .metadata_container import MetadataContainer
from .metadata_provider import MetadataProvider
from .field_metadata import BaseFieldMetadata, PropertyFieldMetadata

# Default metadata provider setup
default_metadata_provider = MetadataProvider()
default_metadata_provider.register_container(CardMetadataContainer())
default_metadata_provider.register_container(SummaryCardUsersMetadataContainer())

__all__ = [
    "CardMetadataContainer",
    "SummaryCardUsersMetadataContainer",
    "BaseFieldMetadata",
    "PropertyFieldMetadata",
    "MetadataContainer", 
    "MetadataProvider",
    "default_metadata_provider",
] 