from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, AsyncSession

from ..config import settings


def get_engine(db_url: str = None) -> Engine:
    if db_url is None:
        db_url = settings.database.url
    return create_engine(db_url)


def get_session_factory(engine: Engine = None) -> sessionmaker:
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, class_=AsyncSession)
