from uuid import UUID
from ...database.models.animestars.card import CardType
from .pagination import BasePaginationQuery, BasePaginationResponse
from .base import BaseSchema
from ...filters import BaseFilter, UUIDEntryFilter, IntegerEntryFilter, StringEntryFilter, EnumEntryFilter, DateTimeEntryFilter
from typing import Literal
from datetime import datetime
from pydantic import field_validator

class CardSchema(BaseSchema):
    id: UUID
    card_id: int
    name: str
    rank: CardType
    anime_name: str | None = None
    anime_link: str | None = None
    author: str | None = None
    image: str | None = None
    mp4: str | None = None
    webm: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("rank", mode="before")
    def validate_rank(cls, v):
        if isinstance(v, str):
            return CardType(v.lower())
        return v


CardSort = Literal[
    "id",
    "card_id",
    "name",
    "rank",
    "anime_name",
    "anime_link",
    "author",
    "image",
    "mp4",
    "webm",
    "created_at",
    "updated_at",
]


class CardFilter(BaseFilter):
    """Filter schema for Card model"""
    id: UUIDEntryFilter | None  = None
    card_id: IntegerEntryFilter | None = None
    name: StringEntryFilter | None = None
    rank: EnumEntryFilter[CardType] | None = None
    anime_name: StringEntryFilter | None = None
    anime_link: StringEntryFilter | None = None
    author: StringEntryFilter | None = None
    image: StringEntryFilter | None = None
    mp4: StringEntryFilter | None = None
    webm: StringEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None


class CardQuery(BasePaginationQuery[CardFilter, CardSort | str]):
    pass


class CardPaginationResponse(BasePaginationResponse[CardSchema]):
    items: list[CardSchema]
