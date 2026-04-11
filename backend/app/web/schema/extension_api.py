from datetime import datetime

from pydantic import Field, create_model

from app.database.enum import CardType
from app.web.schema.base import BaseSchema


_MAX_BATCH = 2000


class ExtensionCardsByImagePathsRequest(BaseSchema):
    images: list[str] = Field(default_factory=list, max_length=_MAX_BATCH)


class ExtensionCardImageResolveItem(BaseSchema):
    image: str
    card_id: int | None = None


class ExtensionDeckRankCountsRequest(BaseSchema):
    card_ids: list[int] = Field(..., max_length=_MAX_BATCH)


DeckRankHistogram = create_model(
    "DeckRankHistogram",
    __base__=BaseSchema,
    **{t.value: (int, Field(default=0)) for t in CardType},
)


class ExtensionOwnerCountsBulkBody(BaseSchema):
    card_ids: list[int] = Field(..., max_length=_MAX_BATCH)
    unlocked: bool = False


class ExtensionOwnerCountsLastItem(BaseSchema):
    """Latest per-collection counts (same source as `/api/card/stats/last/bulk`); each metric has its own `updated_at`."""

    card_id: int
    need: int | None = None
    need_updated_at: datetime | None = None
    owner: int | None = None
    owner_updated_at: datetime | None = None
    trade: int | None = None
    trade_updated_at: datetime | None = None
    unlocked: int | None = None
    unlocked_updated_at: datetime | None = None
