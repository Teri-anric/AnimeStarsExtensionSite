import time
from uuid import UUID
from typing import ClassVar
from sqlalchemy import select, text
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from .crud import CRUDRepository
from .pagination import PaginationRepository

_BULK_CACHE_TTL = 5.0  # seconds


class CardUsersStatsRepository(
    CRUDRepository[CardUsersStats, UUID],
    PaginationRepository[CardUsersStats],
    BaseRepository,
):
    _bulk_cache: ClassVar[dict[tuple[int, ...], tuple[float, list]]] = {}

    @property
    def entry_class(self) -> type[CardUsersStats]:
        return CardUsersStats

    @property
    def entry_code(self) -> str:
        return "card_users_stats"

    async def get_last_card_users_stats(
        self, card_id: int
    ) -> list[CardUsersStats]:        
        results = await self.scalars(
            select(
                CardUsersStats
            )
            .where(
                CardUsersStats.card_id == card_id
            )
            .order_by(CardUsersStats.collection, CardUsersStats.created_at.desc())
            .distinct(CardUsersStats.collection)
        )
        return results

    async def get_last_card_users_stats_bulk(
        self, card_ids: list[int]
    ) -> list[CardUsersStats]:
        cache_key = tuple(sorted(card_ids))
        now = time.monotonic()
        cached = self._bulk_cache.get(cache_key)
        if cached is not None and now - cached[0] < _BULK_CACHE_TTL:
            return cached[1]

        results = await self.scalars(
            select(CardUsersStats)
            .where(CardUsersStats.card_id.in_(card_ids))
            .order_by(CardUsersStats.card_id, CardUsersStats.collection, CardUsersStats.created_at.desc())
            .distinct(CardUsersStats.card_id, CardUsersStats.collection)
        )
        self._bulk_cache[cache_key] = (now, results)
        return results

    async def aggregate_stats_per_second(self, older_than_days: int = 7) -> int:
        """
        Aggregate stats so that, for rows older than N days, there is at most
        one record per (owner_id, card_id, collection, second).

        This reduces the number of points when users generate multiple events
        within the same second.
        """
        sql = text(
            """
            WITH to_aggregate AS (
                SELECT
                    id,
                    owner_id,
                    card_id,
                    collection,
                    created_at,
                    count,
                    date_trunc('second', created_at) AS created_at_sec
                FROM animestars_card_users_stats
                WHERE created_at < now() - (:days || ' days')::interval
            ),
            aggregated AS (
                SELECT
                    owner_id,
                    card_id,
                    collection,
                    created_at_sec AS created_at,
                    ROUND(AVG(count)) AS avg_count
                FROM to_aggregate
                GROUP BY owner_id, card_id, collection, created_at_sec
            ),
            deleted AS (
                DELETE FROM animestars_card_users_stats
                WHERE id IN (SELECT id FROM to_aggregate)
            )
            INSERT INTO animestars_card_users_stats (
                owner_id,
                card_id,
                collection,
                count,
                created_at
            )
            SELECT
                owner_id,
                card_id,
                collection,
                avg_count,
                created_at
            FROM aggregated;
            """
        )

        async with self.auto_commit() as session:
            result = await session.execute(sql, {"days": older_than_days})
            # rowcount may be -1 depending on the driver, but return it if available
            return getattr(result, "rowcount", -1)
