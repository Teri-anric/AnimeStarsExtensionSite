from __future__ import annotations
from typing import Generic, TypeVar, Any, Union, List, Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_serializer

T = TypeVar('T')


class BaseEntryFilter(BaseModel, Generic[T]):
    """Base filter class for all field types"""
    eq: Optional[T] = Field(None, description="Equal to")
    ne: Optional[T] = Field(None, description="Not equal to")
    is_null: Optional[bool] = Field(None, description="Is null/not null")

    model_config = ConfigDict(extra='forbid')


class StringEntryFilter(BaseEntryFilter[str]):
    """String field filters"""
    contains: Optional[str] = Field(None, description="Contains substring")
    icontains: Optional[str] = Field(None, description="Contains substring (case insensitive)")
    like: Optional[str] = Field(None, description="SQL LIKE pattern")
    ilike: Optional[str] = Field(None, description="SQL LIKE pattern (case insensitive)")
    not_like: Optional[str] = Field(None, description="SQL NOT LIKE pattern")
    startswith: Optional[str] = Field(None, description="Starts with")
    endswith: Optional[str] = Field(None, description="Ends with")
    in_: Optional[List[str]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[str]] = Field(None, description="Not in list")


class NumericEntryFilter(BaseEntryFilter[T]):
    """Numeric field filters"""
    gt: Optional[T] = Field(None, description="Greater than")
    gte: Optional[T] = Field(None, description="Greater than or equal")
    lt: Optional[T] = Field(None, description="Less than")
    lte: Optional[T] = Field(None, description="Less than or equal")
    between: Optional[List[T]] = Field(None, description="Between two values")
    in_: Optional[List[T]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[T]] = Field(None, description="Not in list")


class DateTimeEntryFilter(BaseEntryFilter[datetime]):
    """DateTime field filters"""
    gt: Optional[datetime] = Field(None, description="Greater than")
    gte: Optional[datetime] = Field(None, description="Greater than or equal")
    lt: Optional[datetime] = Field(None, description="Less than")
    lte: Optional[datetime] = Field(None, description="Less than or equal")
    before: Optional[datetime] = Field(None, description="Before datetime")
    after: Optional[datetime] = Field(None, description="After datetime")
    between: Optional[List[datetime]] = Field(None, description="Between two datetimes")
    in_: Optional[List[datetime]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[datetime]] = Field(None, description="Not in list")


class DateEntryFilter(BaseEntryFilter[date]):
    """Date field filters"""
    gt: Optional[date] = Field(None, description="Greater than")
    gte: Optional[date] = Field(None, description="Greater than or equal")
    lt: Optional[date] = Field(None, description="Less than")
    lte: Optional[date] = Field(None, description="Less than or equal")
    before: Optional[date] = Field(None, description="Before date")
    after: Optional[date] = Field(None, description="After date")
    between: Optional[List[date]] = Field(None, description="Between two dates")
    in_: Optional[List[date]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[date]] = Field(None, description="Not in list")


class EnumEntryFilter(BaseEntryFilter[T]):
    """Enum field filters with proper serialization"""
    in_: Optional[List[T]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[T]] = Field(None, description="Not in list")
    
    @field_serializer('eq', 'ne', when_used='always')
    def serialize_single_enum(self, value):
        """Serialize single enum value to its name"""
        if isinstance(value, Enum):
            return value.name
        return value
    
    @field_serializer('in_', 'not_in', when_used='always')
    def serialize_enum_list(self, value):
        """Serialize list of enum values to their names"""
        if isinstance(value, list):
            return [v.name if isinstance(v, Enum) else v for v in value]
        return value


class UUIDEntryFilter(BaseEntryFilter[UUID]):
    """UUID field filters"""
    in_: Optional[List[UUID]] = Field(None, alias="in", description="In list")
    not_in: Optional[List[UUID]] = Field(None, description="Not in list")


class BooleanEntryFilter(BaseEntryFilter[bool]):
    """Boolean field filters"""
    pass  # Only has eq, ne, is_null from base


class IntegerEntryFilter(NumericEntryFilter[int]):
    """Integer field filters"""
    pass


class FloatEntryFilter(NumericEntryFilter[float]):
    """Float field filters"""
    pass


class LogicalOperators(BaseModel):
    """Logical operators for complex filtering"""
    and_: Optional[List['BaseFilter']] = Field(None, alias="and", description="AND operator")
    or_: Optional[List['BaseFilter']] = Field(None, alias="or", description="OR operator")
    not_: Optional['BaseFilter'] = Field(None, alias="not", description="NOT operator")
    
    model_config = ConfigDict(extra='forbid')


class BaseFilter(LogicalOperators):
    """Base filter class that can be extended for specific models"""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert filter to dictionary for processing"""
        return self.model_dump(exclude_none=True, by_alias=True)
    
    @classmethod
    def get_supported_fields(cls) -> List[str]:
        """Get list of supported filter fields"""
        return [field for field in cls.model_fields.keys() if not field.startswith('_')]



# Convenience type aliases
StringFilter = Optional[StringEntryFilter]
IntFilter = Optional[IntegerEntryFilter]
FloatFilter = Optional[FloatEntryFilter]
BoolFilter = Optional[BooleanEntryFilter]
UUIDFilter = Optional[UUIDEntryFilter]
DateTimeFilter = Optional[DateTimeEntryFilter]
DateFilter = Optional[DateEntryFilter]
EnumFilter = Optional[EnumEntryFilter]


class ArrayEntryFilter(BaseModel, Generic[T]):
    """Base filter for array/collection relationships"""
    
    length: Optional['IntegerEntryFilter'] = Field(None, description="Filter by number of items")
    any: Optional[T] = Field(None, description="Filter applied to any item in the collection")
    all: Optional[T] = Field(None, description="Filter applied to all items in the collection")
    
    model_config = ConfigDict(extra='forbid')
