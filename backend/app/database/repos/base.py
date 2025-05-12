from abc import ABC
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from ..connection import get_session_factory
from typing import Any


class BaseRepository(ABC):
    __Session: AsyncSession | None = None
    __session: AsyncSession | None = None

    @property
    def Session(self) -> type[AsyncSession]:
        if BaseRepository.__Session is None:
            BaseRepository.__Session = get_session_factory()
        return BaseRepository.__Session

    @property
    def session(self) -> AsyncSession:
        if self.__session is None:
            self.__session = self.Session()
        return self.__session
    
    @asynccontextmanager
    async def auto_commit(self):
        session = self.session
        yield session
        await session.commit()

    async def execute(self, stmt: Select):
        async with self.session as session:
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
