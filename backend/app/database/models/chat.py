from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDPKMixin, TimestampMixin


class ChatMessage(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "chat_messages"

    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, file, image, etc.
    file_url = Column(String, nullable=True)  # URL to file stored separately
    reply_to_id = Column(UUID, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
    reply_to = relationship("ChatMessage", remote_side="ChatMessage.id")
    replies = relationship("ChatMessage", back_populates="reply_to")
    mentions = relationship("ChatMention", back_populates="message", cascade="all, delete-orphan")


class ChatMention(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "chat_mentions"

    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="mentions")
    message = relationship("ChatMessage", back_populates="mentions") 