from sqlalchemy import func, select
from sqlalchemy.orm import relationship

from ..base import Base
from .card import Card


class AnimestarsCardDeck(Base):
    """Model for animestars card decks"""

    __table__ = (
        select(
            Card.anime_link.label("anime_link"),
            Card.anime_name.label("anime_name"),
            func.count(Card.id).label("card_count"),
        )
        .where(Card.anime_link.isnot(None))
        .group_by(Card.anime_link, Card.anime_name)
        .cte("animestarts_card_deck")
    )

    __mapper_args__ = {
        "primary_key": [__table__.c.anime_link, __table__.c.anime_name]  # composite PK
    }

    anime_link: str = __table__.c.anime_link
    anime_name: str = __table__.c.anime_name
    card_count: int = __table__.c.card_count

    cards = relationship(
        Card,
        primaryjoin="AnimestarsCardDeck.anime_link == Card.anime_link",
        foreign_keys="Card.anime_link",
        uselist=True,
        viewonly=True,
    )
