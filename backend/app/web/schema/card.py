from pydantic import Field
from uuid import UUID
from ...database.models.animestars.card import CardType
from ...database.enum import CardCollection, SummaryCardState
from .pagination import BasePaginationQuery, BasePaginationResponse
from .base import BaseSchema
from typing import Literal
from ...database.types.filter import EntryFilter, EnumFliedFilter, StringFieldFilter
from datetime import datetime

class CardSchema(BaseSchema):
    id: UUID
    card_id: int
    name: str
    rank: CardType
    anime_name: str | None
    anime_link: str | None
    author: str | None
    image: str | None
    mp4: str | None
    webm: str | None

    created_at: datetime | None
    updated_at: datetime | None


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
]


class CardFilter(EntryFilter):
    id: EnumFliedFilter[UUID] | None = Field(default=None, description="Filter by ID of the card")
    card_id: EnumFliedFilter[int] | None = Field(default=None, description="Filter by Card ID of the card")
    name: StringFieldFilter | None = Field(default=None, description="Filter by Name of the card")
    rank: EnumFliedFilter[CardType] | None = Field(default=None, description="Filter by Rank of the card")
    anime_name: StringFieldFilter | None = Field(
        default=None, description="Filter by Anime Name of the card"
    )   
    anime_link: StringFieldFilter | None = Field(
        default=None, description="Filter by Anime Link of the card"
    )
    author: StringFieldFilter | None = Field(
        default=None, description="Filter by Author of the card"
    )
    image: StringFieldFilter | None = Field(default=None, description="Filter by Image of the card")
    mp4: StringFieldFilter | None = Field(default=None, description="Filter by MP4 of the card")
    webm: StringFieldFilter | None = Field(default=None, description="Filter by WebM of the card")



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
