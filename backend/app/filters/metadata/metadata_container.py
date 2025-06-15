from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from sqlalchemy import Select


if TYPE_CHECKING:
    from .field_metadata import BaseFieldMetadata
    from ..models.field_filters import FieldFilter
else:
    BaseFieldMetadata = object
    FieldFilter = object


class MetadataContainer(ABC):
    """Container that holds field metadata for a specific model/entity"""

    def __init__(self):
        self._field_metadata: dict[str, BaseFieldMetadata] = {}

    @abstractmethod
    def get_entity_code(self) -> str:
        """Get the entity code for the container"""
        pass

    @property
    def entity_code(self) -> str:
        """Get the entity code for the container"""
        return self.get_entity_code()

    def add_field(self, field_metadata: BaseFieldMetadata) -> "MetadataContainer":
        """Add field metadata to the container using its property_code"""
        self._field_metadata[field_metadata.property_code()] = field_metadata
        return self

    def get_field_metadata(self, property_code: str) -> BaseFieldMetadata | None:
        """Get field metadata by property code"""
        return self._field_metadata.get(property_code)

    def has_field(self, property_code: str) -> bool:
        """Check if field exists in metadata"""
        return property_code in self._field_metadata

    def get_all_fields(self) -> dict[str, BaseFieldMetadata]:
        """Get all field metadata"""
        return self._field_metadata.copy()

    def apply_field_filter(
        self, stmt: Select, property_code: str, field_filter: FieldFilter
    ) -> Select:
        """Apply a field filter using the appropriate metadata"""
        field_metadata = self.get_field_metadata(property_code)
        if field_metadata is None:
            raise ValueError(
                f"Field '{property_code}' not found in metadata for entity '{self.entity_code}'"
            )

        return field_metadata.apply_filter(stmt, field_filter)
