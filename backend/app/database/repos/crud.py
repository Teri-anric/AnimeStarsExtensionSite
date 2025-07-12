from typing import Generic, TypeVar, Iterable
from abc import ABC, abstractmethod

from sqlalchemy import select, delete, update

from .base import BaseRepository


T = TypeVar("T")
K = TypeVar("K")


class CRUDRepository(BaseRepository, Generic[T, K], ABC):
    @property
    @abstractmethod
    def entry_class(self) -> type[T]:
        raise NotImplementedError

    async def create(self, **kwargs) -> T:
        return await self.add(self.entry_class(**kwargs))
    
    async def create_bulk(self, objs: Iterable[T]) -> None:
        await self.add_bulk(objs)

    async def get(self, id: K) -> T | None:
        return await self.scalar(
            select(self.entry_class).where(self.entry_class.id.__eq__(id))
        )

    async def get_all(self) -> list[T]:
        stmt = select(self.entry_class)
        return await self.scalars(stmt)

    async def delete(self, id: K) -> bool:
        obj = await self.get(id)
        if obj:
            await self.execute(
                delete(self.entry_class).where(self.entry_class.id.__eq__(id))
            )
            return True
        return False

    async def update(self, id: K, **kwargs) -> int:
        async with self.auto_commit() as session:
            result = await session.execute(
                update(self.entry_class)
                .where(self.entry_class.id.__eq__(id))
                .values(**kwargs)
            )
            return result.rowcount

