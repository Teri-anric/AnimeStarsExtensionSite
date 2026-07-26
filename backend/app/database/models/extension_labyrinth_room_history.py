from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPKMixin


class ExtensionLabyrinthRoomHistory(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "extension_labyrinth_room_history"

    room_id = mapped_column(
        ForeignKey("extension_labyrinth_rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event: Mapped[str] = mapped_column(String(80), nullable=False)
    is_emission: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
