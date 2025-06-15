from abc import ABC, abstractmethod
from sqlalchemy.sql.elements import ClauseElement
from typing import Any


class BaseResolver(ABC):
    """Base interface for all resolvers"""
    
    @abstractmethod
    def resolve(self, filter_obj: Any, context: Any) -> ClauseElement | None:
        """Resolve filter to SQL condition"""
        pass 