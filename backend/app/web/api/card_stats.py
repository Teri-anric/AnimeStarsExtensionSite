from fastapi import APIRouter
from datetime import UTC

from app.web.schema.card_stats import (
    CardUsersStatsSchema,
    CardUsersStatsQuery,
    CardUsersStatsResponse,
    CardUsersStatsAddRequest,
    CardUsersStatsAddResponse,
)
from app.web.deps import CardUsersStatsRepositoryDep
from app.web.auth.deps import UserDep
from app.database.models.animestars.card_users_stats import CardUsersStats


router = APIRouter(prefix="/card/stats", tags=["card-stats"])


@router.get("/last")
async def get_last_card_users_stats(
    card_id: int,
    repo: CardUsersStatsRepositoryDep,
) -> list[CardUsersStatsSchema]:
    return await repo.get_last_card_users_stats(card_id)


@router.get("/last/bulk")
async def get_last_card_users_stats_bulk(
    card_ids: list[int],
    repo: CardUsersStatsRepositoryDep,
) -> list[CardUsersStatsSchema]:
    return await repo.get_last_card_users_stats_bulk(card_ids)


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
    user: UserDep,
) -> CardUsersStatsAddResponse:
    objs = (
        CardUsersStats(
            owner_id=user.id,
            card_id=stat.card_id,
            collection=stat.collection,
            count=stat.count,
            created_at=stat.created_at.astimezone(UTC).replace(tzinfo=None),
        )
        for stat in request.stats
    )
    await repo.create_bulk(objs)
    return CardUsersStatsAddResponse(
        status="ok",
        message=f"Added {len(request.stats)} card users stats",
    )
