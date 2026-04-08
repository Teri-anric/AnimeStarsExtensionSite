from fastapi import APIRouter, Query
from datetime import UTC
import logging

from app.web.schema.card_stats import (
    CardUsersStatsSchema,
    CardUsersStatsQuery,
    CardUsersStatsResponse,
    CardUsersStatsAddRequest,
    CardUsersStatsAddResponse,
)
from app.web.deps import CardUsersStatsRepositoryDep, CardStatsCacheServiceDep
from app.database.models.animestars.card_users_stats import CardUsersStats


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/card/stats", tags=["card-stats"])


@router.get("/last")
async def get_last_card_users_stats(
    card_id: int,
    repo: CardUsersStatsRepositoryDep,
) -> list[CardUsersStatsSchema]:
    return await repo.get_last_card_users_stats(card_id)


@router.get("/last/bulk")
async def get_last_card_users_stats_bulk(
    repo: CardUsersStatsRepositoryDep,
    cache_service: CardStatsCacheServiceDep,
    card_ids_comma_separated: str = Query(
        ..., description="Comma-separated list of card IDs"
    ),
) -> list[CardUsersStatsSchema]:
    card_ids = list(map(int, card_ids_comma_separated.split(",")))
    return await cache_service.get_last_bulk(repo, card_ids)


@router.post("/")
async def get_card_users_stats_by_card_id(
    query: CardUsersStatsQuery,
    repo: CardUsersStatsRepositoryDep,
) -> CardUsersStatsResponse:
    return await repo.search(query.build())


@router.post("/add")
async def add_card_users_stats(
    request: CardUsersStatsAddRequest,
    repo: CardUsersStatsRepositoryDep,
    cache_service: CardStatsCacheServiceDep,
    # user: UserDep,
) -> CardUsersStatsAddResponse:
    normalized_events = [
        {
            "card_id": stat.card_id,
            "collection": stat.collection,
            "count": stat.count,
            "created_at": stat.created_at.astimezone(UTC).replace(tzinfo=None),
        }
        for stat in request.stats
    ]
    objs = (
        CardUsersStats(
            owner_id=None,
            card_id=event["card_id"],
            collection=event["collection"],
            count=event["count"],
            created_at=event["created_at"],
        )
        for event in normalized_events
    )
    await repo.create_bulk(objs)
    try:
        await cache_service.refresh_after_add(normalized_events)
    except Exception:
        # Cache refresh is best-effort; DB write already succeeded.
        logger.exception("Failed to refresh card stats cache after add")
    return CardUsersStatsAddResponse(
        status="ok",
        message=f"Added {len(request.stats)} card users stats",
    )
