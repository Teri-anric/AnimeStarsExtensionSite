from abc import ABC
from pydantic import BaseModel, Field
from typing import Any, Generic, TypeVar, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .entry_filters import BaseEntryFilter

T = TypeVar("T")


class FieldFilter(ABC, BaseModel):
    """Base class for field-specific filters - pure data model"""
    pass


class StringFieldFilter(FieldFilter):
    """Filter for string fields"""
    eq: str | None = None
    ne: str | None = None
    like: str | None = None
    ilike: str | None = None  # case-insensitive like
    not_like: str | None = None
    contains: str | None = None
    icontains: str | None = None
    not_contains: str | None = None
    in_: list[str] | None = Field(None, alias="in")
    not_in: list[str] | None = None
    is_null: bool | None = None


class NumericFieldFilter(FieldFilter):
    """Filter for numeric fields"""
    eq: int | float | None = None
    ne: int | float | None = None
    gt: int | float | None = None
    lt: int | float | None = None
    gte: int | float | None = None
    lte: int | float | None = None
    in_: list[int | float] | None = Field(None, alias="in")
    not_in: list[int | float] | None = None
    is_null: bool | None = None


class BooleanFieldFilter(FieldFilter):
    """Filter for boolean fields"""
    eq: bool | None = None
    is_null: bool | None = None


class EnumFieldFilter(FieldFilter, Generic[T]):
    """Filter for enum fields"""
    eq: T | None = None
    ne: T | None = None
    in_: list[T] | None = Field(None, alias="in")
    not_in: list[T] | None = None
    is_null: bool | None = None


class ArrayFieldFilter(FieldFilter, Generic[T]):
    """Filter for array/list fields containing submodels (joins)"""
    # Filter for arrays that contain elements matching criteria
    any_: T | None = Field(None, alias="any", description="Array contains any element matching these criteria")
    all_: T | None = Field(None, alias="all", description="Array contains only elements matching these criteria")
    none_: T | None = Field(None, alias="none", description="Array contains no elements matching these criteria")
    
    # Basic array operations
    is_empty: bool | None = None
    is_not_empty: bool | None = None
    size_eq: int | None = None
    size_gt: int | None = None
    size_lt: int | None = None
    size_gte: int | None = None
    size_lte: int | None = None
    
    # For null checks on the entire array
    is_null: bool | None = None 