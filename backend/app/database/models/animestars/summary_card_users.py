import uuid

from sqlalchemy import Column, ForeignKey, Enum, Integer, UUID
from sqlalchemy.orm import relationship

from ..base import Base, TimestampMixin
from ...enum import CardCollection, SummaryCardState


class SummaryCardUsers(Base, TimestampMixin):
    __tablename__ = "animestars_summary_card_users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    card_id: int = Column(Integer, ForeignKey("animestars_cards.card_id"), nullable=False, index=True)
    collection: CardCollection = Column(Enum(CardCollection), nullable=False, index=True)

    state: SummaryCardState = Column(Enum(SummaryCardState), nullable=False)

    count: int = Column(Integer, nullable=False)

    # card = relationship(
    #     "animestars_cards",
    #     # back_populates="summary_card_users",
    # )
