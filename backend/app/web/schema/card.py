from pydantic import Field
from uuid import UUID
from ...database.models.animestars.card import CardType
from ...database.enum import CardCollection, SummaryCardState
from .pagination import BasePaginationQuery, BasePaginationResponse
from .base import BaseSchema
from typing import Literal
from ...database.types.filter import Filter, AndFilter, FilterProperty
from ...database.types.order_by import OrderBy


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


class CardFilter(BaseSchema):
    id: UUID = Field(default=None, description="Filter by ID of the card")
    card_id: int = Field(default=None, description="Filter by Card ID of the card")
    name: str = Field(default=None, description="Filter by Name of the card")
    rank: CardType = Field(default=None, description="Filter by Rank of the card")
    anime_name: str | None = Field(
        default=None, description="Filter by Anime Name of the card"
    )   
    anime_link: str | None = Field(
        default=None, description="Filter by Anime Link of the card"
    )
    author: str | None = Field(
        default=None, description="Filter by Author of the card"
    )
    image: str | None = Field(default=None, description="Filter by Image of the card")
    mp4: str | None = Field(default=None, description="Filter by MP4 of the card")
    webm: str | None = Field(default=None, description="Filter by WebM of the card")

    def build_filter(self) -> Filter:
        filters = []
        items = {
            "id": self.id,
            "card_id": self.card_id,
            "name": self.name,
            "rank": self.rank,
            "anime_name": self.anime_name,
            "anime_link": self.anime_link,
            "author": self.author,
            "image": self.image,
            "mp4": self.mp4,
            "webm": self.webm,
        }
        for key, value in items.items():
            if value is None:
                continue
            filters.append(FilterProperty(property=key, operator=FilterProperty.Operator.EQ, value=value))

        return AndFilter(filters=filters)


class CardQuery(BasePaginationQuery, CardFilter):
    sort: CardSort | None = Field(default=None, description="Sort by the card")

    def build_order_by(self) -> OrderBy | None:
        if self.sort is None:
            return None
        prop, *args = self.sort.split(" ")
        direction = OrderBy.Sort.Direction.DESC
        if "asc" in args:
            direction = OrderBy.Sort.Direction.ASC
        return OrderBy(sorts=[OrderBy.Sort(property=prop, direction=direction)])


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
