import uuid

from sqlalchemy import Column, String, Enum, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ...enum import CardType, CardCollection
from ..base import Base, TimestampMixin
from .user import AnimestarsUser
from .summary_card_users import SummaryCardUsers


class Card(Base, TimestampMixin):
    __tablename__ = "animestars_cards"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    card_id: int = Column(Integer, nullable=False, index=True, unique=True)

    name: str = Column(String, nullable=False)
    rank: CardType = Column(Enum(CardType), nullable=False)

    anime_name: str = Column(String, nullable=True)
    anime_link: str = Column(String, nullable=True)

    author: str = Column(ForeignKey(AnimestarsUser.username), nullable=True)

    image: str = Column(String, nullable=False)
    mp4: str = Column(String, nullable=True)
    webm: str = Column(String, nullable=True)

    summary_card_users = relationship(
        SummaryCardUsers,
        back_populates="card",
        cascade="all, delete",
    )

    author_user = relationship(
        AnimestarsUser,
        foreign_keys=[author],
        back_populates="author_cards",
    )

    owner_users = relationship(
        AnimestarsUser,
        secondary="animestars_card_users",
        primaryjoin="animestars_card_users.card_id == animestars_cards.id",
        secondaryjoin=f"animestars_card_users.collection == {CardCollection.OWNED.name}",
    )
    trade_users = relationship(
        AnimestarsUser,
        secondary="animestars_card_users",
        primaryjoin="animestars_card_users.card_id == animestars_cards.id",
        secondaryjoin=f"animestars_card_users.collection == {CardCollection.TRADE.name}",
    )
    need_users = relationship(
        AnimestarsUser,
        secondary="animestars_card_users",
        primaryjoin="animestars_card_users.card_id == animestars_cards.id",
        secondaryjoin=f"animestars_card_users.collection == {CardCollection.NEED.name}",
    )
