from __future__ import annotations
from typing import Generic, TypeVar, Any, Self
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_serializer

T = TypeVar('T')


class BaseEntryFilter(BaseModel, Generic[T]):
    """Base filter class for all field types"""
    eq: T | None = Field(None, description="Equal to")
    ne: T | None = Field(None, description="Not equal to")
    is_null: bool | None = Field(None, description="Is null/not null")

    model_config = ConfigDict(extra='forbid')


class StringEntryFilter(BaseEntryFilter[str]):
    """String field filters"""
    contains: str | None = Field(None, description="Contains substring")
    icontains: str | None = Field(None, description="Contains substring (case insensitive)")
    like: str | None = Field(None, description="SQL LIKE pattern")
    ilike: str | None = Field(None, description="SQL LIKE pattern (case insensitive)")
    not_like: str | None = Field(None, description="SQL NOT LIKE pattern")
    startswith: str | None = Field(None, description="Starts with")
    endswith: str | None = Field(None, description="Ends with")
    in_: list[str] | None = Field(None, alias="in", description="In list")
    not_in: list[str] | None = Field(None, description="Not in list")


class NumericEntryFilter(BaseEntryFilter[T]):
    """Numeric field filters"""
    gt: T | None = Field(None, description="Greater than")
    gte: T | None = Field(None, description="Greater than or equal")
    lt: T | None = Field(None, description="Less than")
    lte: T | None = Field(None, description="Less than or equal")
    between: list[T] | None = Field(None, description="Between two values")
    in_: list[T] | None = Field(None, alias="in", description="In list")
    not_in: list[T] | None = Field(None, description="Not in list")


class DateTimeEntryFilter(BaseEntryFilter[datetime]):
    """DateTime field filters"""
    gt: datetime | None = Field(None, description="Greater than")
    gte: datetime | None = Field(None, description="Greater than or equal")
    lt: datetime | None = Field(None, description="Less than")
    lte: datetime | None = Field(None, description="Less than or equal")
    before: datetime | None = Field(None, description="Before datetime")
    after: datetime | None = Field(None, description="After datetime")
    between: list[datetime] | None = Field(None, description="Between two datetimes")
    in_: list[datetime] | None = Field(None, alias="in", description="In list")
    not_in: list[datetime] | None = Field(None, description="Not in list")


class DateEntryFilter(BaseEntryFilter[date]):
    """Date field filters"""
    gt: date | None = Field(None, description="Greater than")
    gte: date | None = Field(None, description="Greater than or equal")
    lt: date | None = Field(None, description="Less than")
    lte: date | None = Field(None, description="Less than or equal")
    before: date | None = Field(None, description="Before date")
    after: date | None = Field(None, description="After date")
    between: list[date] | None = Field(None, description="Between two dates")
    in_: list[date] | None = Field(None, alias="in", description="In list")
    not_in: list[date] | None = Field(None, description="Not in list")


class EnumEntryFilter(BaseEntryFilter[T]):
    """Enum field filters with proper serialization"""
    in_: list[T] | None = Field(None, alias="in", description="In list")
    not_in: list[T] | None = Field(None, description="Not in list")
    
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
    in_: list[UUID] | None = Field(None, alias="in", description="In list")
    not_in: list[UUID] | None = Field(None, description="Not in list")


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
    and_: list[Self] | None = Field(None, alias="and", description="AND operator")
    or_: list[Self] | None = Field(None, alias="or", description="OR operator")
    not_: Self | None = Field(None, alias="not", description="NOT operator")
    
    model_config = ConfigDict(extra='forbid')


class BaseFilter(LogicalOperators):
    """Base filter class that can be extended for specific models"""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert filter to dictionary for processing"""
        return self.model_dump(exclude_none=True, by_alias=True)
    
    @classmethod
    def get_supported_fields(cls) -> list[str]:
        """Get list of supported filter fields"""
        return [field for field in cls.model_fields.keys() if not field.startswith('_')]



# Convenience type aliases
StringFilter = StringEntryFilter | None
IntFilter = IntegerEntryFilter | None
FloatFilter = FloatEntryFilter | None
BoolFilter = BooleanEntryFilter | None
UUIDFilter = UUIDEntryFilter | None
DateTimeFilter = DateTimeEntryFilter | None
DateFilter = DateEntryFilter | None
EnumFilter = EnumEntryFilter | None


class ArrayEntryFilter(BaseModel, Generic[T]):
    """Base filter for array/collection relationships"""
    
    length: IntegerEntryFilter | None = Field(None, description="Filter by number of items")
    any: T | None = Field(None, description="Filter applied to any item in the collection")
    all: T | None = Field(None, description="Filter applied to all items in the collection")
    
    model_config = ConfigDict(extra='forbid')
