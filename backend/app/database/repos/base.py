from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Type
from ..connection  import get_session_factory
from ..models.base import Base


class BaseRepository(ABC):
    __Session: Session = None

    @property
    def Session(self) -> Session:
        if self.__Session is None:
            self.__Session = get_session_factory()
        return self.__Session

    @property
    def session(self) -> Session:
        return self.Session()
