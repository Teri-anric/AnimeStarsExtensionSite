from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ...enum import CardType, CardCollection
from ..base import Base
from .user import AnimestarsUser


class Card(Base):
    __tablename__ = "animestars_cards"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(String, nullable=False)
    rank: CardType = Column(Enum(CardType), nullable=False)

    anime_name: str = Column(String, nullable=True)
    anime_link: str = Column(String, nullable=True)

    author: str = Column(ForeignKey(AnimestarsUser.username), nullable=True)

    image: str = Column(String, nullable=False)
    mp4: str = Column(String, nullable=True)
    webm: str = Column(String, nullable=True)

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
