from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPKMixin


class ExtensionLabyrinthRoom(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "extension_labyrinth_rooms"
    __table_args__ = (UniqueConstraint("x", "y", name="uq_extension_labyrinth_rooms_xy"),)

    x: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    y: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    # Stable room type observed outside an emission.
    event = Column(String(80), nullable=True)
    sources_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # An emission can temporarily change the room. It must not overwrite `event`
    # until it is known whether that state is shared by every player.
    emission_event = Column(String(80), nullable=True)
    emission_sources_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    emission_observed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
