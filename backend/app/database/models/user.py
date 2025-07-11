from datetime import datetime, timedelta, UTC
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, UUIDPKMixin, TimestampMixin
from ...config import settings

def default_expire_at():
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.auth.access_token_expire_minutes)
    return expire_at.replace(tzinfo=None)

class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username = Column(
        String,
        ForeignKey("animestars_users.username", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class Token(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "tokens"

    is_active = Column(Boolean, default=True)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    expire_at = Column(DateTime, nullable=True, default=default_expire_at)

    def get_access_token(self) -> str:
        from ...web.auth.utils import create_access_token

        access_token = create_access_token(
            data={
                "sub": str(self.id),
                "userid": str(self.user_id),
            },
            expire=self.expire_at,
        )
        return access_token
