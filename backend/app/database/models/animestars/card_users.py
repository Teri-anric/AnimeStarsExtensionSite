from sqlalchemy import Column, String, ForeignKey, Enum, Integer
from ..base import Base
from ...enum import CardCollection, CardState
from .card import Card
from .user import AnimestarsUser


class CardUsers(Base):
    __tablename__ = "animestars_card_users"

    id: int = Column(Integer, primary_key=True)

    card_id: int = Column(Integer, ForeignKey(Card.id), nullable=False, index=True)
    user_username: str = Column(String, ForeignKey(AnimestarsUser.username), nullable=False, index=True)
    collection: CardCollection = Column(Enum(CardCollection), nullable=False, index=True)

    state: CardState | None = Column(Enum(CardState), nullable=True)
