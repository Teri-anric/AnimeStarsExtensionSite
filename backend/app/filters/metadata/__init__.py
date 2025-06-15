from .card_metadata import CardMetadataContainer
from .field_metadata import BaseFieldMetadata, PropertyFieldMetadata
from .metadata_container import MetadataContainer
from .metadata_provider import MetadataProvider

# Default metadata provider setup
default_metadata_provider = MetadataProvider()
default_metadata_provider.register_container(CardMetadataContainer())

__all__ = [
    "CardMetadataContainer",
    "BaseFieldMetadata",
    "PropertyFieldMetadata",
    "MetadataContainer", 
    "MetadataProvider",
    "default_metadata_provider",
] 