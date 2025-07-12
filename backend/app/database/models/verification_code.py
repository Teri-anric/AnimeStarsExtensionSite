from datetime import datetime, timedelta, UTC
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, UUIDPKMixin
from ...config import settings


def default_expire_at():
    expire_at = datetime.now(UTC) + timedelta(hours=settings.pm.code_expire_hours)
    return expire_at.replace(tzinfo=None)


class VerificationCode(UUIDPKMixin, Base):
    __tablename__ = "verification_codes"

    username = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    expire_at = Column(DateTime, nullable=False, default=default_expire_at)
    is_used = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC).replace(tzinfo=None) > self.expire_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired and self.is_active