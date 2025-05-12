from .base import BaseSchema
from typing import Generic, TypeVar

T = TypeVar("T")


class BasePaginationQuery(BaseSchema):
    page: int = 1
    per_page: int = 50


class BasePaginationResponse(BaseSchema, Generic[T]):
    total: int
    page: int
    per_page: int
    items: list[T]
    total_pages: int
    has_next: bool
