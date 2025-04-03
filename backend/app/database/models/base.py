from sqlalchemy import Column, Integer, String, DateTime, func, MetaData, UUID
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    metadata = MetaData()


class UUIDPKMixin:
    id: UUID = Column(UUID, primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: DateTime = Column(DateTime, default=func.now())
    updated_at: DateTime = Column(DateTime, default=func.now(), onupdate=func.now())
