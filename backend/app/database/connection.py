from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

from ..config import settings


def get_engine(db_url: str = None) -> AsyncEngine:
    if db_url is None:
        db_url = settings.database.url
    return create_async_engine(db_url)


def get_session_factory(engine: AsyncEngine = None) -> sessionmaker:
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, class_=AsyncSession)
