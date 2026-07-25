from __future__ import annotations

import html
import logging
from collections import defaultdict

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse

from app.database.enum import CardCollection
from app.database.models.animestars.card_users_stats import CardUsersStats
from app.database.repos.user import TokenRepository
from app.web.auth.deps import UserDep
from app.web.deps import (
    CardRepositoryDep,
    CardStatsCacheServiceDep,
    CardUsersStatsRepositoryDep,
    ExtensionBannerRepositoryDep,
    ExtensionCardImageCacheServiceDep,
    ExtensionLabyrinthRoomRepositoryDep,
)
from app.web.schema.auth import Token
from app.web.schema.extension_api import (
    ExtensionBannerConfigResponse,
    ExtensionLabyrinthBulkRoomsRequest,
    ExtensionLabyrinthBulkRoomsResponse,
    ExtensionLabyrinthMapResponse,
    ExtensionLabyrinthRoomItem,
    ExtensionLabyrinthSummaryResponse,
    DeckRankHistogram,
    ExtensionCardImageResolveItem,
    ExtensionCardsByImagePathsRequest,
    ExtensionDeckRankCountsRequest,
    ExtensionOwnerCountsBulkBody,
    ExtensionOwnerCountsLastItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extension", tags=["extension"])


def _owner_item_from_stats(
    card_id: int,
    stats_for_card: list[CardUsersStats],
    include_unlocked: bool,
) -> ExtensionOwnerCountsLastItem:
    by_col: dict[CardCollection, CardUsersStats] = {}
    for s in stats_for_card:
        cur = by_col.get(s.collection)
        if cur is None or s.created_at >= cur.created_at:
            by_col[s.collection] = s

    need = by_col.get(CardCollection.NEED)
    owned = by_col.get(CardCollection.OWNED)
    trade = by_col.get(CardCollection.TRADE)
    unlocked_s = by_col.get(CardCollection.UNLOCKED_OWNED)

    item = ExtensionOwnerCountsLastItem(card_id=card_id)
    if need is not None:
        item.need = need.count
        item.need_updated_at = need.updated_at
    if owned is not None:
        item.owner = owned.count
        item.owner_updated_at = owned.updated_at
    if trade is not None:
        item.trade = trade.count
        item.trade_updated_at = trade.updated_at
    if include_unlocked and unlocked_s is not None:
        item.unlocked = unlocked_s.count
        item.unlocked_updated_at = unlocked_s.updated_at
    return item


def _build_iframe_html(config: ExtensionBannerConfigResponse) -> str:
    if not config.is_active:
        return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: transparent; }
    </style>
  </head>
  <body></body>
</html>
"""

    title = html.escape(config.title)
    message = html.escape(config.message)
    action_text = html.escape(config.action_text) if config.action_text else ""
    action_url = html.escape(config.action_url or "", quote=True)
    cta_html = (
        f'<a class="banner-link" target="_blank" rel="noopener noreferrer" href="{action_url}">{action_text}</a>'
        if config.action_text and config.action_url
        else ""
    )

    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root {{
        color-scheme: dark;
      }}
      html, body {{
        margin: 0;
        width: 100%;
      }}
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: transparent;
        padding: 8px;
        box-sizing: border-box;
      }}
      .banner {{
        border: 1px solid #6f253f;
        background: linear-gradient(90deg, #2f1220 0%, #1b1a2d 100%);
        border-radius: 12px;
        color: #f5f6ff;
        padding: 12px;
      }}
      .banner-title {{
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 4px;
      }}
      .banner-message {{
        font-size: 13px;
        line-height: 1.4;
        opacity: 0.92;
      }}
      .banner-link {{
        margin-top: 8px;
        display: inline-block;
        color: #f79dbb;
        text-decoration: none;
        font-size: 13px;
        font-weight: 600;
      }}
      .banner-link:hover {{
        text-decoration: underline;
      }}
    </style>
  </head>
  <body>
    <div class="banner">
      <div class="banner-title">{title}</div>
      <div class="banner-message">{message}</div>
      {cta_html}
    </div>
  </body>
</html>
"""


@router.post("/token", response_model=Token)
async def get_extension_token(
    current_user: UserDep,
    token_repo: TokenRepository = Depends(lambda: TokenRepository()),
) -> Token:
    """
    Generate a new authentication token for the browser extension.

    This endpoint creates a new token using the same system as regular user login,
    allowing the extension to authenticate API requests on behalf of the user.
    """
    try:
        token = await token_repo.create(user_id=current_user.id, expire_at=None)

        logger.info("Extension token created for user %s", current_user.username)

        return Token(
            access_token=token.get_access_token(),
            token_type="bearer",
        )

    except Exception as e:
        logger.exception("Error creating extension token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create extension token",
        ) from e


@router.post("/cards/by-image-paths", response_model=list[ExtensionCardImageResolveItem])
async def extension_cards_by_image_paths(
    body: ExtensionCardsByImagePathsRequest,
    card_repo: CardRepositoryDep,
    img_cache: ExtensionCardImageCacheServiceDep,
) -> list[ExtensionCardImageResolveItem]:
    """Resolve `card_id` from stored image paths (Redis + DB)."""
    resolved = await img_cache.resolve_images(card_repo, body.images)
    return [ExtensionCardImageResolveItem(image=img, card_id=cid) for img, cid in resolved]


@router.post(
    "/decks/rank-counts",
    response_model=dict[str, DeckRankHistogram],
)
async def extension_deck_rank_counts(
    body: ExtensionDeckRankCountsRequest,
    card_repo: CardRepositoryDep,
) -> dict[str, DeckRankHistogram]:
    """Per-card rank histogram for the deck that card belongs to (no full `deck.cards`)."""
    counts = await card_repo.deck_rank_counts_by_reference_card_ids(body.card_ids)
    return {str(k): DeckRankHistogram.model_validate(v) for k, v in counts.items()}


@router.post(
    "/cards/owner-counts/last/bulk",
    response_model=list[ExtensionOwnerCountsLastItem],
    response_model_exclude_none=True,
)
async def extension_owner_counts_last_bulk_post(
    body: ExtensionOwnerCountsBulkBody,
    stats_repo: CardUsersStatsRepositoryDep,
    cache_service: CardStatsCacheServiceDep,
) -> list[ExtensionOwnerCountsLastItem]:
    """Same as GET bulk when the ID list is too long for a query string."""
    stats = await cache_service.get_last_bulk(stats_repo, body.card_ids)
    by_card: dict[int, list[CardUsersStats]] = defaultdict(list)
    for s in stats:
        by_card[s.card_id].append(s)
    return [
        _owner_item_from_stats(cid, by_card.get(cid, []), body.unlocked)
        for cid in body.card_ids
    ]


@router.get("/banner-config", response_model=ExtensionBannerConfigResponse)
async def extension_banner_config(
    banner_repo: ExtensionBannerRepositoryDep,
) -> ExtensionBannerConfigResponse:
    banner = await banner_repo.get_or_create()
    return ExtensionBannerConfigResponse(
        title=banner.title,
        message=banner.message,
        action_text=banner.action_text,
        action_url=banner.action_url,
        is_active=banner.is_active,
    )


@router.get("/banner-iframe", response_class=HTMLResponse)
async def extension_banner_iframe(
    banner_repo: ExtensionBannerRepositoryDep,
) -> HTMLResponse:
    banner = await banner_repo.get_or_create()
    if not banner.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner is not active")
    config = ExtensionBannerConfigResponse(
        title=banner.title,
        message=banner.message,
        action_text=banner.action_text,
        action_url=banner.action_url,
        is_active=banner.is_active,
    )
    return HTMLResponse(content=_build_iframe_html(config))


@router.get("/labyrinth/map", response_model=ExtensionLabyrinthMapResponse)
async def extension_labyrinth_map(
    labyrinth_repo: ExtensionLabyrinthRoomRepositoryDep,
    min_x: int = Query(..., ge=-100000, le=100000),
    max_x: int = Query(..., ge=-100000, le=100000),
    min_y: int = Query(..., ge=-100000, le=100000),
    max_y: int = Query(..., ge=-100000, le=100000),
    updated_after: datetime | None = None,
) -> ExtensionLabyrinthMapResponse:
    if min_x > max_x or min_y > max_y:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bounds")
    if (max_x - min_x + 1) * (max_y - min_y + 1) > 20000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bounds are too large")

    rooms = await labyrinth_repo.list_map(
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        updated_after=updated_after,
    )
    return ExtensionLabyrinthMapResponse(
        rooms=[
            ExtensionLabyrinthRoomItem(
                x=room.x,
                y=room.y,
                event=room.event,
                sources_count=room.sources_count,
                updated_at=room.updated_at,
            )
            for room in rooms
        ]
    )


@router.get("/labyrinth/map/summary", response_model=ExtensionLabyrinthSummaryResponse)
async def extension_labyrinth_map_summary(
    labyrinth_repo: ExtensionLabyrinthRoomRepositoryDep,
) -> ExtensionLabyrinthSummaryResponse:
    return ExtensionLabyrinthSummaryResponse.model_validate(await labyrinth_repo.summary())


@router.post("/labyrinth/rooms/bulk", response_model=ExtensionLabyrinthBulkRoomsResponse)
async def extension_labyrinth_rooms_bulk(
    body: ExtensionLabyrinthBulkRoomsRequest,
    labyrinth_repo: ExtensionLabyrinthRoomRepositoryDep,
) -> ExtensionLabyrinthBulkRoomsResponse:
    count = await labyrinth_repo.bulk_upsert([room.model_dump() for room in body.rooms])
    return ExtensionLabyrinthBulkRoomsResponse(count=count)
