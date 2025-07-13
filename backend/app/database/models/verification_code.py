from sqlalchemy import Column, String, Boolean, ForeignKey

from .base import Base, UUIDPKMixin, TimestampMixin


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
