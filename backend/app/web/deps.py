from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database.connection import get_engine, get_session_factory
from app.config import settings


def get_db() -> AsyncSession:
    engine = get_engine(settings.database.url)
    session_factory = get_session_factory(engine)
    return session_factory()

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
