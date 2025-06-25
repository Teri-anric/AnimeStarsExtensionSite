from fastapi import APIRouter

from app.web.schema.card_stats import (
    CardUsersStatsSchema,
    CardUsersStatsQuery,
    CardUsersStatsResponse,
)
from app.web.deps import CardUsersStatsRepositoryDep

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
) -> CardUsersStatsSchema:
    return await repo.get_card_users_stats(query.card_id)
