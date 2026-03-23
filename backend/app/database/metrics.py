"""SQLAlchemy + Postgres stats exposed as Prometheus metrics (Grafana via Prometheus datasource)."""

from __future__ import annotations

import asyncio
import logging
import time

from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings

logger = logging.getLogger(__name__)

QUERY_DURATION = Histogram(
    "sqlalchemy_query_duration_seconds",
    "DB round-trip time per cursor execute (SQLAlchemy → asyncpg)",
    buckets=(0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

QUERIES_TOTAL = Counter(
    "sqlalchemy_queries_executed_total",
    "Executed SQL statements (grouped by leading keyword)",
    ["kind"],
)

POOL_CHECKED_OUT = Gauge(
    "sqlalchemy_pool_connections_checked_out",
    "Connections currently checked out from the pool",
)
POOL_CHECKED_IN = Gauge(
    "sqlalchemy_pool_connections_idle",
    "Idle connections available in the pool",
)
POOL_OVERFLOW = Gauge(
    "sqlalchemy_pool_overflow",
    "Overflow connections beyond configured pool size",
)
POOL_OPEN_TOTAL = Gauge(
    "sqlalchemy_pool_connections_open",
    "Total connections currently opened by the pool",
)

PG_NUM_BACKENDS = Gauge(
    "postgres_stat_database_num_backends",
    "Backends attached to this database (pg_stat_database)",
)
PG_XACT_COMMIT = Gauge(
    "postgres_stat_database_xact_commit",
    "Cumulative commits for this DB (use delta() / rate over range in PromQL)",
)
PG_XACT_ROLLBACK = Gauge(
    "postgres_stat_database_xact_rollback",
    "Cumulative rollbacks for this DB",
)
PG_BLKS_READ = Gauge(
    "postgres_stat_database_blks_read",
    "Cumulative disk blocks read",
)
PG_BLKS_HIT = Gauge(
    "postgres_stat_database_blks_hit",
    "Cumulative shared buffer hits",
)

_instrumented_sync_engine_ids: set[int] = set()


def _statement_kind(statement: str) -> str:
    s = (statement or "").lstrip().upper()
    if not s:
        return "OTHER"
    if s.startswith("WITH") or s.startswith("SELECT"):
        return "SELECT"
    if s.startswith("INSERT"):
        return "INSERT"
    if s.startswith("UPDATE"):
        return "UPDATE"
    if s.startswith("DELETE"):
        return "DELETE"
    return "OTHER"


def instrument_engine(async_engine: AsyncEngine) -> None:
    """Listen on the sync engine used under the async API (one registration per process)."""
    sync_eng = async_engine.sync_engine
    eid = id(sync_eng)
    if eid in _instrumented_sync_engine_ids:
        return
    _instrumented_sync_engine_ids.add(eid)

    @event.listens_for(sync_eng, "before_cursor_execute")
    def _before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("_sqla_q_stack", []).append(time.monotonic())

    @event.listens_for(sync_eng, "after_cursor_execute")
    def _after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        stack = conn.info.get("_sqla_q_stack")
        if stack:
            t0 = stack.pop()
            QUERY_DURATION.observe(time.monotonic() - t0)
        QUERIES_TOTAL.labels(kind=_statement_kind(statement)).inc()

    @event.listens_for(sync_eng, "handle_error")
    def _handle_error(exception_context):
        conn = getattr(exception_context, "connection", None)
        if conn is None or not hasattr(conn, "info"):
            return
        stack = conn.info.get("_sqla_q_stack")
        if stack:
            stack.pop()


def _update_pool_gauges(async_engine: AsyncEngine) -> None:
    pool = async_engine.sync_engine.pool
    POOL_CHECKED_OUT.set(pool.checkedout())
    POOL_CHECKED_IN.set(pool.checkedin())
    POOL_OVERFLOW.set(pool.overflow())
    POOL_OPEN_TOTAL.set(pool.size())


async def _refresh_pg_stats(async_engine: AsyncEngine) -> None:
    if not settings.db_metrics_pg_stats:
        return
    async with async_engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT numbackends, xact_commit, xact_rollback, blks_read, blks_hit
                FROM pg_stat_database
                WHERE datname = current_database()
                """
            )
        )
        row = result.one()
        PG_NUM_BACKENDS.set(row[0])
        PG_XACT_COMMIT.set(row[1])
        PG_XACT_ROLLBACK.set(row[2])
        PG_BLKS_READ.set(row[3])
        PG_BLKS_HIT.set(row[4])


async def metrics_refresh_loop(async_engine: AsyncEngine) -> None:
    interval = settings.db_metrics_refresh_seconds
    while True:
        try:
            _update_pool_gauges(async_engine)
            await _refresh_pg_stats(async_engine)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("db metrics refresh failed")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise


def start_metrics_background_task(async_engine: AsyncEngine) -> asyncio.Task[None]:
    return asyncio.create_task(metrics_refresh_loop(async_engine))
