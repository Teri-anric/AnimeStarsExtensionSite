from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPKMixin


class ExtensionLabyrinthRoom(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "extension_labyrinth_rooms"
    __table_args__ = (UniqueConstraint("x", "y", name="uq_extension_labyrinth_rooms_xy"),)

    x: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    y: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event = Column(String(80), nullable=True)
    sources_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
