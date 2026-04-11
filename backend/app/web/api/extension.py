from __future__ import annotations

import logging
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.enum import CardCollection
from app.database.models.animestars.card_users_stats import CardUsersStats
from app.database.repos.user import TokenRepository
from app.web.auth.deps import ProtectedDep, UserDep
from app.web.deps import (
    CardRepositoryDep,
    CardStatsCacheServiceDep,
    CardUsersStatsRepositoryDep,
    ExtensionCardImageCacheServiceDep,
)
from app.web.schema.auth import Token
from app.web.schema.extension_api import (
    DeckRankHistogram,
    ExtensionCardImageResolveItem,
    ExtensionCardsByImagePathsRequest,
    ExtensionDeckRankCountsRequest,
    ExtensionOwnerCountsBulkBody,
    ExtensionOwnerCountsLastItem,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extension", tags=["extension"], dependencies=[ProtectedDep])


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
