import uuid

from sqlalchemy import Column, String, UUID, Index, func
from sqlalchemy.orm import relationship

from ..base import Base, TimestampMixin


class AnimestarsUser(Base, TimestampMixin):
    __tablename__ = "animestars_users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    username: str = Column(String, unique=True, nullable=False)

    # author_cards = relationship(
    #     "animestars_cards",
    #     primaryjoin="Card.author == AnimestarsUser.username",
    # )

    __table_args__ = (
        Index("idx_animestars_users_username", func.lower(username), unique=True),
    )
