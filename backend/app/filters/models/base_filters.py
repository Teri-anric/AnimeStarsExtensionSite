from abc import ABC
from pydantic import BaseModel
from typing import Any, Self


class BaseFilter(ABC, BaseModel):
    """Base class for all filters - pure data model without logic"""
    pass


class CombinedFilter(BaseFilter):
    """Filter that combines multiple filters with AND/OR operators"""
    operator: str  # "and" or "or"
    filters: list[BaseFilter]


class NotFilter(BaseFilter):
    """Filter that negates another filter"""
    filter: BaseFilter


class RawFilter(BaseFilter):
    """Filter for raw SQL conditions"""
    statement: Any 