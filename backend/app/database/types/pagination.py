from typing import TypeVar, Generic, Dict, Any

from pydantic import BaseModel, ConfigDict

from .order_by import OrderBy

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total: int
    page: int
    per_page: int
    items: list[T]

    @property
    def total_pages(self) -> int:
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


class PaginationQuery(BaseModel):
    page: int = 1
    per_page: int = 10

    order_by: OrderBy | None = None
    filter: Dict[str, Any] | None = None
