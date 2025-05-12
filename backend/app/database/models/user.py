from datetime import timedelta
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, UUIDPKMixin, TimestampMixin
from ...config import settings


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

    def get_access_token(self) -> str:
        from ...web.auth.utils import create_access_token

        access_token_expires = timedelta(
            minutes=settings.auth.access_token_expire_minutes
        )   
        access_token = create_access_token(
            data={
                "sub": str(self.id),
                "userid": str(self.user_id),
            },
            expires_delta=access_token_expires,
        )
        return access_token
