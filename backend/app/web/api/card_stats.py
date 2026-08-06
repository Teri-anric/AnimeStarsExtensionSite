from fastapi import APIRouter, Query
from datetime import UTC

from app.web.schema.card_stats import (
    CardUsersStatsSchema,
    CardUsersStatsCurrentSchema,
    CardUsersStatsQuery,
    CardUsersStatsResponse,
    CardUsersStatsAddRequest,
    CardUsersStatsAddResponse,
)
from app.web.deps import CardUsersStatsRepositoryDep, CardRepositoryDep

router = APIRouter(prefix="/card/stats", tags=["card-stats"])


@router.get("/last")
async def get_last_card_users_stats(
    card_id: int,
    repo: CardRepositoryDep,
) -> list[CardUsersStatsCurrentSchema]:
    return await repo.get_current_stats([card_id])


@router.get("/last/bulk")
async def get_last_card_users_stats_bulk(
    repo: CardRepositoryDep,
    card_ids_comma_separated: str = Query(
        ..., description="Comma-separated list of card IDs"
    ),
) -> list[CardUsersStatsCurrentSchema]:
    card_ids = list(map(int, card_ids_comma_separated.split(",")))
    return await repo.get_current_stats(card_ids)


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
    await repo.add_stats_and_update_current(normalized_events)
    return CardUsersStatsAddResponse(
        status="ok",
        message=f"Added {len(request.stats)} card users stats",
    )
