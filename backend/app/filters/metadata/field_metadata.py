from abc import ABC, abstractmethod
from sqlalchemy import Column, Select
from sqlalchemy.orm import aliased
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.entry_filters import BaseEntryFilter


class BaseFieldMetadata(ABC):
    """Base class for field metadata"""
    
    @abstractmethod
    def get_column(self, alias=None) -> Column:
        """Get the SQLAlchemy column for this field, optionally with alias"""
        pass
    
    @abstractmethod
    def get_field_name(self) -> str:
        """Get the field name"""
        pass


class PropertyFieldMetadata(BaseFieldMetadata):
    """Metadata for a direct model property field"""
    
    def __init__(self, column: Column, field_name: str):
        self._column = column
        self._field_name = field_name
    
    def get_column(self, alias=None) -> Column:
        """Get the column, using alias if provided"""
        if alias is not None:
            return getattr(alias, self._field_name)
        return self._column
    
    def get_field_name(self) -> str:
        return self._field_name
    
    def property_code(self) -> str:
        """Get the property code (same as field name)"""
        return self._field_name


class BaseJoinHandler(ABC):
    """Abstract class for handling joins"""
    
    @property
    @abstractmethod
    def alias(self):
        """Get the SQLAlchemy alias for the joined table"""
        pass
    
    @abstractmethod
    def prepare_query(self, stmt: Select, parent_alias=None) -> Select:
        """Prepare query by adding necessary JOINs with parent alias context"""
        pass 