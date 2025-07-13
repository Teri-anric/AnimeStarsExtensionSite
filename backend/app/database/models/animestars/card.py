from sqlalchemy import (
    Column,
    String,
    Enum,
    ForeignKey,
    Integer,
    select,
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from ...enum import CardType, CardCollection
from ..base import Base, TimestampMixin, UUIDPKMixin
from .user import AnimestarsUser
from .card_users_stats import CardUsersStats


class Card(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "animestars_cards"

    card_id: int = Column(Integer, nullable=False, index=True, unique=True)

    name: str = Column(String, nullable=False)
    rank: CardType = Column(Enum(CardType), nullable=False)

    anime_name: str = Column(String, nullable=True)
    anime_link: str = Column(String, nullable=True)

    author: str = Column(String, ForeignKey(AnimestarsUser.username), nullable=True)

    # Relationship to access the author user object
    author_user = relationship("AnimestarsUser", foreign_keys=[author], lazy="select")

    image: str = Column(String, nullable=True)
    mp4: str = Column(String, nullable=True)
    webm: str = Column(String, nullable=True)

    stats_count = column_property(
        select(func.count(CardUsersStats.id)).where(CardUsersStats.card_id == card_id)
    )
