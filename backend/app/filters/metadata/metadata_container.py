from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from sqlalchemy import Select


if TYPE_CHECKING:
    from .field_metadata import BaseFieldMetadata, BaseJoinHandler
    from ..models.entry_filters import BaseEntryFilter
else:
    BaseFieldMetadata = object
    BaseEntryFilter = object
    BaseJoinHandler = object


class MetadataContainer(ABC):
    """Container that holds field metadata for a specific model/entity"""

    def __init__(self):
        self._field_metadata: dict[str, BaseFieldMetadata] = {}

    @abstractmethod
    def get_entity_code(self) -> str:
        """Get the entity code for the container"""
        pass

    def get_field_metadata(self, property_code: str) -> BaseFieldMetadata | None:
        """Get field metadata by property code"""
        return self._field_metadata.get(property_code)
    
    def get_join(self, property_code: str) -> BaseJoinHandler | None:
        """Get join handler for property code - implement in subclasses"""
        return None

    @abstractmethod
    def prepare_query(self, stmt: Select, entry_filter: BaseEntryFilter) -> Select:
        """
        Prepare query by adding necessary JOINs based on the filter.
        This is where the metadata container handles relationships and JOINs.
        Subclasses must implement this method.
        """
        return stmt

    def add_field(self, field_metadata: BaseFieldMetadata) -> "MetadataContainer":
        """Add field metadata to the container using its property_code"""
        self._field_metadata[field_metadata.property_code()] = field_metadata
        return self
