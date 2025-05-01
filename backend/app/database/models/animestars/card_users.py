import uuid

from sqlalchemy import Column, String, ForeignKey, Enum, Integer, UUID
from ..base import Base, TimestampMixin
from ...enum import CardCollection, CardState
from .card import Card
from .user import AnimestarsUser


class CardUsers(Base, TimestampMixin):
    __tablename__ = "animestars_card_users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    card_id: int = Column(Integer, ForeignKey(Card.id), nullable=False, index=True)
    user_username: str = Column(String, ForeignKey(AnimestarsUser.username), nullable=False, index=True)
    collection: CardCollection = Column(Enum(CardCollection), nullable=False, index=True)

    state: CardState | None = Column(Enum(CardState), nullable=True)
