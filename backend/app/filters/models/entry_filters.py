from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Self, ClassVar

class BaseEntryFilter(ABC, BaseModel):
    """Base class for entry-specific filters - pure data model"""
    
    # Metadata
    entry_code: ClassVar[str]
    
    # Logical operators
    and_: list[Self] | None = Field(None, alias="and")
    or_: list[Self] | None = Field(None, alias="or")
    
    @classmethod
    @abstractmethod
    def get_entry_code(cls) -> str:
        """Return the entry code to identify which metadata container to use"""
        pass 