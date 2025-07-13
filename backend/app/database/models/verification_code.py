from datetime import datetime, timedelta, UTC
from sqlalchemy import Column, String, Boolean, ForeignKey, func
from sqlalchemy.orm import column_property
from .base import Base, UUIDPKMixin, TimestampMixin

from app.config import settings


class VerificationCode(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "verification_codes"

    username = Column(
        String,
        ForeignKey("animestars_users.username", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    code = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)

    @column_property
    @classmethod
    def is_valid(cls):
        return (
            cls.created_at
            + timedelta(minutes=settings.auth.code_expire_minutes)
        ) > func.now()
