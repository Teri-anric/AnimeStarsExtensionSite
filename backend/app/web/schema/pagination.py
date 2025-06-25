from .base import BaseSchema
from typing import Generic, TypeVar
from pydantic import Field
from ...filters.models import BaseEntryFilter
from ...database.types.order_by import OrderBy
from ...database.types.pagination import PaginationQuery

T = TypeVar("T")
F = TypeVar("F", bound=BaseEntryFilter)
S = TypeVar("S")


class SortGeneric(BaseSchema, Generic[S]):
    property: S
    direction: OrderBy.Sort.Direction

    def to_sort(self) -> OrderBy.Sort:
        return OrderBy.Sort(property=self.property, direction=self.direction)

class BasePaginationQuery(BaseSchema, Generic[F, S]):
    filter: F | None = Field(default=None, description="Filter by the pagination")
    order_by: S | None | list[SortGeneric[S]] = Field(default=None, description="Order by the pagination")
    page: int = 1
    per_page: int = 50

    def old_build_order_by(self) -> OrderBy | None:
        if self.order_by is None:
            return None
        prop, *args = self.order_by.split(" ")
        direction = OrderBy.Sort.Direction.DESC
        if "asc" in args:
            direction = OrderBy.Sort.Direction.ASC
        return OrderBy(sorts=[OrderBy.Sort(property=prop, direction=direction)])

    def build_order_by(self) -> OrderBy | None:
        if isinstance(self.order_by, str):
            return self.old_build_order_by()
        if self.order_by is None:
            return None
        return OrderBy(sorts=[sort.to_sort() for sort in self.order_by])

    def build(self):
        return PaginationQuery(
            page=self.page,
            per_page=self.per_page,
            filter=self.filter,
            order_by=self.build_order_by(),
        )


class BasePaginationResponse(BaseSchema, Generic[T]):
    total: int
    page: int
    per_page: int
    items: list[T]
    total_pages: int
    has_next: bool
