from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, AsyncSession


def get_engine(db_url: str) -> Engine:
    return create_engine(db_url)


def get_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, class_=AsyncSession)
