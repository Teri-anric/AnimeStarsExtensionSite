from uuid import UUID
from sqlalchemy import select, text, bindparam, ARRAY, Integer
from ..models.animestars.card_users_stats import CardUsersStats
from .base import BaseRepository
from .crud import CRUDRepository
from .pagination import PaginationRepository


class CardUsersStatsRepository(
    CRUDRepository[CardUsersStats, UUID],
    PaginationRepository[CardUsersStats],
    BaseRepository,
):
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
        stmt = select(CardUsersStats).from_statement(self._BULK_SQL)
        async with self.session as session:
            result = await session.execute(stmt, {"card_ids": card_ids})
            return list(result.scalars().all())

    async def aggregate_stats_per_second(self, older_than_days: int = 7) -> int:
        """
        Aggregate duplicate stats so that, for rows older than N days, there is
        at most one record per (owner_id, card_id, collection, second).

        Only duplicate groups are touched. The former DELETE + INSERT rewrote
        every old row, competed with the card flush for locks, and raw SQL did
        not have an ORM-generated UUID for the replacement row.
        """
        sql = text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    owner_id,
                    card_id,
                    collection,
                    date_trunc('second', created_at) AS created_at_sec,
                    ROUND(AVG(count) OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                    ))::integer AS avg_count,
                    COUNT(*) OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                    ) AS group_count,
                    ROW_NUMBER() OVER (
                        PARTITION BY owner_id, card_id, collection, date_trunc('second', created_at)
                        ORDER BY created_at, id
                    ) AS row_number
                FROM animestars_card_users_stats
                WHERE created_at < now() - make_interval(days => :days)
            ),
            updated AS (
                UPDATE animestars_card_users_stats AS stats
                SET count = ranked.avg_count,
                    created_at = ranked.created_at_sec
                FROM ranked
                WHERE stats.id = ranked.id
                  AND ranked.row_number = 1
                  AND ranked.group_count > 1
                RETURNING stats.id
            ),
            deleted AS (
                DELETE FROM animestars_card_users_stats AS stats
                USING ranked
                WHERE stats.id = ranked.id
                  AND ranked.row_number > 1
                RETURNING stats.id
            )
            SELECT
                (SELECT count(*) FROM updated) + (SELECT count(*) FROM deleted) AS affected;
            """
        ).bindparams(bindparam("days", type_=Integer))

        async with self.auto_commit() as session:
            result = await session.execute(sql, {"days": older_than_days})
            return int(result.scalar_one())
