from sqlalchemy import Column, String, Index, func

from ..base import Base, TimestampMixin, UUIDPKMixin


class AnimestarsUser(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "animestars_users"

    username: str = Column(String, unique=True, nullable=False)

    __table_args__ = (
        Index("idx_animestars_users_username", func.lower(username), unique=True),
    )
