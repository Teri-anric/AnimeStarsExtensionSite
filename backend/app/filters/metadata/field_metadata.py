from abc import ABC, abstractmethod
from sqlalchemy import Column
from typing import Any


class BaseFieldMetadata(ABC):
    """Base class for field metadata"""
    
    @abstractmethod
    def get_column(self) -> Column:
        """Get the SQLAlchemy column for this field"""
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
    
    def get_column(self) -> Column:
        return self._column
    
    def get_field_name(self) -> str:
        return self._field_name
    
    def property_code(self) -> str:
        """Get the property code (same as field name)"""
        return self._field_name
    
    def apply_filter(self, stmt, field_filter):
        """Apply field filter to SQL statement"""
        # This method will be implemented by the field resolver
        # For now, just return the statement unchanged
        return stmt 