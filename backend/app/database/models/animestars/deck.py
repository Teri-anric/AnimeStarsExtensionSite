from sqlalchemy import Column, String, select, func
from sqlalchemy.orm import relationship, column_property

from ..base import Base, UUIDPKMixin, TimestampMixin
from .card import Card


class AnimestarsDeck(Base, UUIDPKMixin, TimestampMixin):
    """One deck per canonical anime name (unique); cards reference deck_id."""

    __tablename__ = "animestars_decks"

    anime_name: str = Column(String, nullable=False, unique=True, index=True)
    anime_link: str | None = Column(String, nullable=True, index=True)

    cards = relationship(
        "Card",
        back_populates="deck",
        foreign_keys="Card.deck_id",
    )

    card_count = column_property(
        select(func.count(Card.id))
        .where(Card.deck_id == id)
        .scalar_subquery()
    )
