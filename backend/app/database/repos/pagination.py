from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from sqlalchemy import select, delete, update, Select, func, asc, desc
from .base import BaseRepository
from ..types.pagination import Pagination, PaginationQuery
from ..types.order_by import OrderBy
from ...filters import filter_service

T = TypeVar("T")

class PaginationRepository(BaseRepository, Generic[T], ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def search(self, query: PaginationQuery, *args, **kwargs) -> Pagination[T]:
        return await self.paginate(select(self.entry_class), query, *args, **kwargs)

    async def paginate(
        self, stmt: Select, query: PaginationQuery, *args, **kwargs
    ) -> Pagination[T]:
        base_stmt = self._apply_filter(stmt, query.filter)

        stmt = self._apply_sorts(base_stmt, query.order_by)
        stmt = self._apply_pagination(stmt, query)
        
        if "total_base_stmt" in kwargs:
            total = await self._total(self._apply_filter(kwargs["total_base_stmt"], query.filter))
        else:
            total = await self._total(base_stmt)

        items = await self._execute_search(stmt, *args, **kwargs)
        if kwargs.get("is_dto", False):
            return Pagination(
                total=total,
                page=query.page,
                per_page=query.per_page,
                items=items,
            )
        return Pagination[T](
            total=total,
            page=query.page,
            per_page=query.per_page,
            items=items,
        )

    async def _execute_search(self, stmt: Select, *args, **kwargs) -> list[T]:
        if kwargs.get("is_dto", False):
            return await self.execute(stmt)
        return await self.scalars(stmt)

    async def _total(self, stmt: Select, *args, **kwargs) -> int:
        return await self.scalar(select(func.count()).select_from(stmt))

    def _apply_sorts(self, stmt: Select, order_by: OrderBy | None) -> Select:
        if not order_by:
            return stmt

        for sort in order_by.sorts:
            if sort.direction == OrderBy.Sort.Direction.ASC:
                stmt = stmt.order_by(asc(sort.property))
            else:
                stmt = stmt.order_by(desc(sort.property))
        
        return stmt

    def _apply_pagination(self, stmt: Select, query: PaginationQuery) -> Select:
        return stmt.offset((query.page - 1) * query.per_page).limit(query.per_page)

    @property
    @abstractmethod
    def entry_class(self) -> type[T]:
        raise NotImplementedError

    def _apply_filter(self, stmt: Select, filter_data: dict | None) -> Select:
        """Apply filter to statement using the new universal filter service"""
        if not filter_data:
            return stmt
            
        return filter_service.apply_filters(stmt, self.entry_class, filter_data)

    async def get_by(self, filter_data: dict) -> list[T]:
        return await self.scalars(self._apply_filter(select(self.entry_class), filter_data))

    async def get_one_by(self, filter_data: dict) -> T | None:
        return await self.scalar(self._apply_filter(select(self.entry_class), filter_data))

    async def delete_by(self, filter_data: dict) -> int:
        result = await self.execute(self._apply_filter(delete(self.entry_class), filter_data))
        return result.rowcount

    async def update_by(self, filter_data: dict, update_by: dict) -> int:
        result = await self.execute(
            self._apply_filter(update(self.entry_class), filter_data).values(**update_by)
        )
        return result.rowcount
