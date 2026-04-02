from abc import ABC
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Select
from ..connection import get_session_factory
from typing import Any, Iterable


class BaseRepository(ABC):
    __Session: sessionmaker[AsyncSession] | None = None

    @property
    def Session(self) -> sessionmaker[AsyncSession]:
        if BaseRepository.__Session is None:
            BaseRepository.__Session = get_session_factory()
        return BaseRepository.__Session

    @property
    def session(self) -> AsyncSession:
        return self.Session()
    
    @asynccontextmanager
    async def auto_commit(self):
        async with self.session as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def execute(self, stmt: Select):
        async with self.auto_commit() as session:
            result = await session.execute(stmt)
            return result

    async def scalar(self, stmt: Select):
        async with self.session as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def scalars(self, stmt: Select):
        async with self.session as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add(self, obj: Any):
        async with self.session as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def add_bulk(self, objs: Iterable[Any]):
        async with self.session as session:
            session.add_all(objs)
            await session.commit()
