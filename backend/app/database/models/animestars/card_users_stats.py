from sqlalchemy import ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPKMixin, OwnerMixin
from ...enum import CardCollection


class CardUsersStats(Base, UUIDPKMixin, OwnerMixin, TimestampMixin):
    __tablename__ = "animestars_card_users_stats"

    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("animestars_cards.card_id"), nullable=False, index=True)
    collection: Mapped[CardCollection] = mapped_column(Enum(CardCollection, name="card_collection"), nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

