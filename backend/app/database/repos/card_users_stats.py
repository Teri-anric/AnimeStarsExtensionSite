import time
from uuid import UUID
from typing import ClassVar
from sqlalchemy import select, text, bindparam, ARRAY, Integer
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

    # Optimized query: LATERAL per (card_id, collection) → 160 index seeks vs full scan
    # Benchmark: ~3ms vs ~670ms (239x) for a 40-card batch
    _BULK_SQL = text("""
        SELECT s.*
        FROM unnest(:card_ids) AS c(cid)
        CROSS JOIN unnest(ARRAY['NEED','OWNED','TRADE','UNLOCKED_OWNED']::card_collection[]) AS col(coll)
        CROSS JOIN LATERAL (
            SELECT *
            FROM animestars_card_users_stats
            WHERE card_id = c.cid AND collection = col.coll
            ORDER BY created_at DESC
            LIMIT 1
        ) s
    """).bindparams(bindparam("card_ids", type_=ARRAY(Integer)))

    async def get_last_card_users_stats_bulk(
        self, card_ids: list[int]
    ) -> list[CardUsersStats]:
        if not card_ids:
            return []

        cache_key = tuple(sorted(card_ids))
        now = time.monotonic()
        cached = self._bulk_cache.get(cache_key)
        if cached is not None and now - cached[0] < _BULK_CACHE_TTL:
            return cached[1]

        stmt = select(CardUsersStats).from_statement(self._BULK_SQL)
        async with self.session as session:
            result = await session.execute(stmt, {"card_ids": card_ids})
            results = list(result.scalars().all())

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
