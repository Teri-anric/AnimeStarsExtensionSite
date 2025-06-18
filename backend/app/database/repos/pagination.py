from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from sqlalchemy import select, delete, update, Select, func
from .base import BaseRepository
from ..types.filter import BaseFilter
from ..types.pagination import Pagination, PaginationQuery
from ..types.order_by import OrderBy
from ...filters import FilterService
from ...filters.setup import default_filter_service
from ...filters.models import BaseEntryFilter

T = TypeVar("T")


class PaginationRepository(BaseRepository, Generic[T], ABC):
    def __init__(self, *args, filter_service: FilterService | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_service = filter_service or default_filter_service

    async def search(self, query: PaginationQuery, *args, **kwargs) -> Pagination[T]:
        return await self.paginate(select(self.entry_class), query, *args, **kwargs)

    async def paginate(
        self, stmt: Select, query: PaginationQuery, *args, **kwargs
    ) -> Pagination[T]:
        base_stmt = self._apply_filter(stmt, query.filter)

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

    def _apply_filter(self, stmt: Select, filter: BaseFilter | BaseEntryFilter | dict | None) -> Select:
        """Apply filter to statement using the filter service"""
        if not filter:
            return stmt
        
        entry_code = getattr(self, 'entry_code', None)
        
        # Use FilterService to prepare query with metadata (handles ArrayFieldFilter and and/or logic)
        stmt = self.filter_service.prepare_query_with_metadata(stmt, filter, entry_code)
        
        # Use filter service to resolve the remaining conditions
        condition = self.filter_service.parse_and_resolve(
            filter_data=filter,
            entry_code=entry_code,
            model_class=self.entry_class
        )
        
        if condition is None:
            return stmt
        return stmt.where(condition)
        
    
    async def get_by(self, filter: BaseFilter | dict) -> list[T]:
        return await self.scalars(self._apply_filter(select(self.entry_class), filter))

    async def get_one_by(self, filter: BaseFilter | dict) -> T | None:
        return await self.scalar(self._apply_filter(select(self.entry_class), filter))

    async def delete_by(self, filter: BaseFilter | dict) -> int:
        result = await self.execute(self._apply_filter(delete(self.entry_class), filter))
        return result.rowcount

    async def update_by(self, filter: BaseFilter | dict, update_by: dict) -> int:
        result = await self.execute(
            self._apply_filter(update(self.entry_class), filter).values(**update_by)
        )
        return result.rowcount
