import uuid

from sqlalchemy import (
    Column,
    String,
    Enum,
    ForeignKey,
    Integer,
    UUID,
    select,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import column_property
from ...enum import CardCollection, CardType
from ..base import Base, TimestampMixin, UUIDPKMixin
from .user import AnimestarsUser
from .card_users_stats import CardUsersStats


def _latest_stat_count_scalar(collection: CardCollection, card_id_col):
    """Most recent `count` for this card and collection (by updated_at, then created_at)."""
    return (
        select(CardUsersStats.count)
        .where(
            CardUsersStats.card_id == card_id_col,
            CardUsersStats.collection == collection,
        )
        .order_by(
            CardUsersStats.created_at.desc(),
        )
        .limit(1)
        .scalar_subquery()
    )


class Card(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "animestars_cards"

    card_id: int = Column(Integer, nullable=False, index=True, unique=True)

    name: str = Column(String, nullable=False)
    rank: CardType = Column(Enum(CardType), nullable=False)

    anime_name: str = Column(String, nullable=True)
    anime_link: str = Column(String, nullable=True)

    deck_id: uuid.UUID | None = Column(
        UUID(as_uuid=True),
        ForeignKey("animestars_decks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    deck = relationship("AnimestarsDeck", back_populates="cards")

    author: str = Column(String, ForeignKey(AnimestarsUser.username), nullable=True)

    # Relationship to access the author user object
    author_user = relationship("AnimestarsUser", foreign_keys=[author], lazy="select")

    image: str = Column(String, nullable=True, index=True)
    mp4: str = Column(String, nullable=True)
    webm: str = Column(String, nullable=True)

    stats_count = column_property(
        select(func.count(CardUsersStats.id)).where(CardUsersStats.card_id == card_id),
        deferred=True,
    )

    trade_count = column_property(
        _latest_stat_count_scalar(CardCollection.TRADE, card_id),
        deferred=True,
    )
    need_count = column_property(
        _latest_stat_count_scalar(CardCollection.NEED, card_id),
        deferred=True,
    )
    owned_count = column_property(
        _latest_stat_count_scalar(CardCollection.OWNED, card_id),
        deferred=True,
    )
    unlocked_owned_count = column_property(
        _latest_stat_count_scalar(CardCollection.UNLOCKED_OWNED, card_id),
        deferred=True,
    )
