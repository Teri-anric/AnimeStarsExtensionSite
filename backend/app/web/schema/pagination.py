from .base import BaseSchema
from typing import Generic, TypeVar
from pydantic import Field
from ...filters.models import BaseEntryFilter
from ...database.types.order_by import OrderBy

T = TypeVar("T")
F = TypeVar("F", bound=BaseEntryFilter)
S = TypeVar("S")


class BasePaginationQuery(BaseSchema, Generic[F, S]):
    filter: F | None = Field(default=None, description="Filter by the pagination")
    order_by: S | None = Field(default=None, description="Order by the pagination")
    page: int = 1
    per_page: int = 50

    def build_order_by(self) -> OrderBy | None:
        if self.order_by is None:
            return None
        prop, *args = self.order_by.split(" ")
        direction = OrderBy.Sort.Direction.DESC
        if "asc" in args:
            direction = OrderBy.Sort.Direction.ASC
        return OrderBy(sorts=[OrderBy.Sort(property=prop, direction=direction)])



class BasePaginationResponse(BaseSchema, Generic[T]):
    total: int
    page: int
    per_page: int
    items: list[T]
    total_pages: int
    has_next: bool
