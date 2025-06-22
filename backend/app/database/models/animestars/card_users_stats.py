from sqlalchemy import Column, ForeignKey, Enum, Integer

from ..base import Base, TimestampMixin, UUIDPKMixin, OwnerMixin
from ...enum import CardCollection


class CardUsersStats(Base, UUIDPKMixin, OwnerMixin, TimestampMixin):
    __tablename__ = "animestars_card_users_stats"

    card_id: int = Column(Integer, ForeignKey("animestars_cards.card_id"), nullable=False, index=True)
    collection: CardCollection = Column(Enum(CardCollection, name="card_collection"), nullable=False, index=True)

    count: int = Column(Integer, nullable=False)

