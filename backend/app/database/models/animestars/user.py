from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from ..base import Base
from .card import Card


class AnimestarsUser(Base):
    __tablename__ = "animestars_users"

    username: str = Column(String, nullable=False, unique=True, primary_key=True)

    author_cards = relationship(
        Card,
        primaryjoin="animestars_card.author == animestars_users.username",
    )
