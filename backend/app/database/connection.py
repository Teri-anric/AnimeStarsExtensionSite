from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

from ..config import settings

_default_engine: AsyncEngine | None = None


def get_engine(db_url: str | None = None) -> AsyncEngine:
    """Return shared async engine when ``db_url`` is omitted (one pool per process)."""
    global _default_engine
    if db_url is not None:
        return create_async_engine(db_url, pool_pre_ping=True)
    if _default_engine is None:
        _default_engine = create_async_engine(
            settings.database.url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=14,
        )
    return _default_engine


def get_session_factory(engine: AsyncEngine = None) -> sessionmaker:
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, class_=AsyncSession)
