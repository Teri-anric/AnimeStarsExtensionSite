from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from ...enum import CardType
from ..base import Base
from .user import AnimestarsUser


class Card(Base):
    __tablename__ = "animestars_cards"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    name: str = Column(String, nullable=False)
    rank: CardType = Column(Enum(CardType), nullable=False)

    anime_name: str = Column(String, nullable=True)
    anime_link: str = Column(String, nullable=True)

    author: str = Column(ForeignKey(AnimestarsUser.username), nullable=True)

    image: str = Column(String, nullable=False)
    mp4: str = Column(String, nullable=True)
    webm: str = Column(String, nullable=True)
