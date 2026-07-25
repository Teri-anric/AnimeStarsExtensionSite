from sqlalchemy import Column, Index, Integer, String, func, select
from sqlalchemy.orm import column_property, declared_attr, relationship

from ..base import Base, UUIDPKMixin, TimestampMixin
from .card import Card


class AnimestarsDeck(Base, UUIDPKMixin, TimestampMixin):
    """One deck per canonical anime name (unique); cards reference deck_id."""

    __tablename__ = "animestars_decks"

    anime_name: str = Column(String, nullable=False, unique=True, index=True)
    anime_link: str | None = Column(String, nullable=True)
    anime_id: int = Column(Integer, nullable=False)

    __table_args__ = (
        Index(
            "uq_animestars_decks_anime_id",
            "anime_id",
            unique=True,
        ),
    )

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
