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


class ExtensionBannerConfigResponse(BaseSchema):
    title: str
    message: str
    action_text: str | None = None
    action_url: str | None = None
    is_active: bool


class ExtensionLabyrinthRoomItem(BaseSchema):
    x: int
    y: int
    event: str | None = None
    sources_count: int
    emission_event: str | None = None
    emission_sources_count: int
    emission_observed_at: datetime | None = None
    updated_at: datetime


class ExtensionLabyrinthMapResponse(BaseSchema):
    rooms: list[ExtensionLabyrinthRoomItem]


class ExtensionLabyrinthSummaryResponse(BaseSchema):
    total_rooms: int
    min_x: int | None = None
    max_x: int | None = None
    min_y: int | None = None
    max_y: int | None = None
    updated_at: datetime | None = None
    events: dict[str, int] = Field(default_factory=dict)


class ExtensionLabyrinthRoomInput(BaseSchema):
    x: int
    y: int
    event: str | None = Field(default=None, max_length=80)
    emission_event: str | None = Field(default=None, max_length=80)


class ExtensionLabyrinthBulkRoomsRequest(BaseSchema):
    rooms: list[ExtensionLabyrinthRoomInput] = Field(default_factory=list, max_length=_MAX_BATCH)


class ExtensionLabyrinthBulkRoomsResponse(BaseSchema):
    status: str = "ok"
    count: int
