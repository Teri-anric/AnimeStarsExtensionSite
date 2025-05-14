from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from sqlalchemy import select, delete, update, Select, func
from .base import BaseRepository
from ..types.filter import Filter
from ..types.pagination import Pagination, PaginationQuery
from ..types.order_by import OrderBy

T = TypeVar("T")


class PaginationRepository(BaseRepository, Generic[T], ABC):
    async def search(self, query: PaginationQuery, *args, **kwargs) -> Pagination[T]:
        return await self.paginate(select(self.entry_class), query, *args, **kwargs)

    async def paginate(
        self, stmt: Select, query: PaginationQuery, *args, **kwargs
    ) -> Pagination[T]:
        base_stmt = self._apply_filters(stmt, query.filter)

        stmt = self._apply_sorts(base_stmt, query.order_by)
        stmt = self._apply_pagination(stmt, query)

        total = await self._total(base_stmt)
        items = await self._execute_search(stmt, *args, **kwargs)
        return Pagination[self.entry_class](
            total=total,
            page=query.page,
            per_page=query.per_page,
            items=items,
        )

    async def _execute_search(self, stmt: Select, *args, **kwargs) -> list[T]:
        return await self.scalars(stmt)

    async def _total(self, stmt: Select, *args, **kwargs) -> int:
        return await self.scalar(select(func.count()).select_from(stmt))

    def _apply_filters(self, stmt: Select, filters: Filter | None) -> Select:
        if filters:
            stmt = stmt.where(filters.apply(self.entry_class))
        return stmt

    def _apply_sorts(self, stmt: Select, order_by: OrderBy | None) -> Select:
        if order_by:
            stmt = stmt.order_by(*order_by.apply(self.entry_class))
        return stmt

    def _apply_pagination(self, stmt: Select, query: PaginationQuery) -> Select:
        return stmt.offset((query.page - 1) * query.per_page).limit(query.per_page)

    @property
    @abstractmethod
    def entry_class(self) -> type[T]:
        raise NotImplementedError


    def _apply_filter(self, stmt: Select, filter: Filter | dict | None) -> Select:
        if filter:
            if isinstance(filter, dict):
                stmt = stmt.filter_by(**filter)
            else:
                stmt = stmt.filter(filter.apply(self.entry_class))
        return stmt
    
    async def get_by(self, filter: Filter) -> list[T]:
        return await self.scalars(self._apply_filter(select(self.entry_class), filter))

    async def get_one_by(self, filter: Filter) -> T | None:
        return await self.scalar(self._apply_filter(select(self.entry_class), filter))

    async def delete_by(self, filter: Filter) -> int:
        result = await self.execute(self._apply_filter(delete(self.entry_class), filter))
        return result.rowcount

    async def update_by(self, filter: Filter, update_by: dict) -> int:
        result = await self.execute(
            self._apply_filter(update(self.entry_class), filter).values(**update_by)
        )
        return result.rowcount
