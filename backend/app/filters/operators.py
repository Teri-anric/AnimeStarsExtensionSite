from enum import Enum
from typing import Any


class EnumHandler:
    """Handles enum conversion for database queries"""
    
    @staticmethod
    def convert_value_for_db(value: Any) -> Any:
        """Convert enum instances to their names for database storage"""
        if isinstance(value, Enum):
            return value.name
        elif isinstance(value, list):
            return [EnumHandler.convert_value_for_db(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(EnumHandler.convert_value_for_db(v) for v in value)
        return value


class FilterOperators:
    """Contains all supported filter operators and their implementations"""
    
    @staticmethod
    def get_operator_map():
        return {
            # String operators
            'eq': lambda col, val: col == EnumHandler.convert_value_for_db(val),
            'ne': lambda col, val: col != EnumHandler.convert_value_for_db(val),
            'contains': lambda col, val: col.contains(EnumHandler.convert_value_for_db(val)),
            'icontains': lambda col, val: col.ilike(f'%{EnumHandler.convert_value_for_db(val)}%'),
            'like': lambda col, val: col.like(EnumHandler.convert_value_for_db(val)),
            'ilike': lambda col, val: col.ilike(EnumHandler.convert_value_for_db(val)),
            'not_like': lambda col, val: ~col.like(EnumHandler.convert_value_for_db(val)),
            'startswith': lambda col, val: col.like(f'{EnumHandler.convert_value_for_db(val)}%'),
            'endswith': lambda col, val: col.like(f'%{EnumHandler.convert_value_for_db(val)}'),
            'in_': lambda col, val: col.in_(EnumHandler.convert_value_for_db(val)),
            'in': lambda col, val: col.in_(EnumHandler.convert_value_for_db(val)),  # Alias
            'not_in': lambda col, val: ~col.in_(EnumHandler.convert_value_for_db(val)),
            'is_null': lambda col, val: col.is_(None) if val else col.is_not(None),
            
            # Numeric operators
            'gt': lambda col, val: col > EnumHandler.convert_value_for_db(val),
            'gte': lambda col, val: col >= EnumHandler.convert_value_for_db(val),
            'lt': lambda col, val: col < EnumHandler.convert_value_for_db(val),
            'lte': lambda col, val: col <= EnumHandler.convert_value_for_db(val),
            
            # Date operators
            'before': lambda col, val: col < EnumHandler.convert_value_for_db(val),
            'after': lambda col, val: col > EnumHandler.convert_value_for_db(val),
            'between': lambda col, val: col.between(
                EnumHandler.convert_value_for_db(val[0]), 
                EnumHandler.convert_value_for_db(val[1])
            ),
        }
    
    @staticmethod
    def get_supported_operators() -> list[str]:
        """Get list of all supported operator names"""
        return list(FilterOperators.get_operator_map().keys()) 