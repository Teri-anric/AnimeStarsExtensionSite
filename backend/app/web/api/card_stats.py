from fastapi import APIRouter
from datetime import UTC, datetime, timedelta

from app.web.schema.card_stats import (
    CardUsersStatsSchema,
    CardUsersStatsQuery,
    CardUsersStatsResponse,
    CardUsersStatsAddRequest,
    CardUsersStatsAddResponse,
    CardUsersStatsLastWithPrevQuery,
    CardUsersStatsLastWithPrevResponse,
    CardUsersStatsWithPrevSchema,
)
from app.web.deps import CardUsersStatsRepositoryDep
from app.web.auth.deps import UserDep, ProtectedDep
from app.database.models.animestars.card_users_stats import CardUsersStats


router = APIRouter(prefix="/card/stats", tags=["card-stats"], dependencies=[ProtectedDep])


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


@router.post("/last-with-prev")
async def get_last_with_previous(
    request: CardUsersStatsLastWithPrevQuery,
    repo: CardUsersStatsRepositoryDep,
) -> CardUsersStatsLastWithPrevResponse:
    # Determine previous period cut-off
    now = datetime.now(UTC).replace(tzinfo=None)
    if request.period == "day":
        delta = timedelta(days=1)
    elif request.period == "week":
        delta = timedelta(weeks=1)
    else:
        delta = timedelta(days=30)

    last = await repo.get_last_card_users_stats(request.card_id)
    prev = await repo.get_last_card_users_stats_before_or_at(request.card_id, now - delta)

    prev_map = { (p.collection): p for p in prev }

    items: list[CardUsersStatsWithPrevSchema] = []
    for l in last:
        prev_item = prev_map.get(l.collection)
        previous_count = prev_item.count if prev_item else None
        delta_count = (l.count - previous_count) if previous_count is not None else None
        items.append(CardUsersStatsWithPrevSchema(
            id=l.id,
            card_id=l.card_id,
            collection=l.collection,
            count=l.count,
            created_at=l.created_at,
            updated_at=l.updated_at,
            previous_count=previous_count,
            delta=delta_count,
        ))

    return CardUsersStatsLastWithPrevResponse(items=items)
