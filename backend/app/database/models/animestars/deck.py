from sqlalchemy import Column, String, select, func
from sqlalchemy.orm import column_property, declared_attr, relationship

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

    @declared_attr
    def card_count(cls):
        return column_property(
            select(func.count(Card.id))
            .where(Card.deck_id == cls.id)
            .correlate_except(Card)
            .scalar_subquery(),
            deferred=True,
        )
