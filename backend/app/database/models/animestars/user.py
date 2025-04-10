from sqlalchemy import Column, String
from ..base import Base


class AnimestarsUser(Base):
    __tablename__ = "animestars_users"

    username: str = Column(String, nullable=False, unique=True, primary_key=True)
