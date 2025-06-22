from pydantic import Field, field_validator
from uuid import UUID
from ...database.models.animestars.card import CardType
from ...database.enum import CardCollection, SummaryCardState
from .pagination import BasePaginationQuery, BasePaginationResponse
from .base import BaseSchema
from typing import Literal
from ...filters.entries.card_filter import CardFilter
from datetime import datetime

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
    "id asc",
    "id desc",
    "id",
    "card_id asc",
    "card_id desc",
    "card_id",
    "name asc",
    "name desc",
    "name",
    "rank asc",
    "rank desc",
    "rank",
    "anime_name asc",
    "anime_name desc",
    "anime_name",
    "anime_link asc",
    "anime_link desc",
    "anime_link",
    "author asc",
    "author desc",
    "author",
    "image asc",
    "image desc",
    "image",
    "mp4 asc",
    "mp4 desc",
    "mp4",
    "webm asc",
    "webm desc",
    "webm",
    "created_at asc",
    "created_at desc",
    "created_at",
    "updated_at asc",
    "updated_at desc",
    "updated_at",
]




# CardFilter is now imported from filters.entries.card_filter

class CardQuery(BasePaginationQuery[CardFilter, CardSort]):
    pass


class CardPaginationResponse(BasePaginationResponse[CardSchema]):
    items: list[CardSchema]


class CardUsersSummarySchema(BaseSchema):
    id: UUID
    card_id: int
    collection: CardCollection
    state: SummaryCardState
    count: int


class CardUsersSummaryResponse(BaseSchema):
    owned: CardUsersSummarySchema | None = None
    trade: CardUsersSummarySchema | None = None
    need: CardUsersSummarySchema | None = None
