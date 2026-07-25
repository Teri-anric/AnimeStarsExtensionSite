from logging import getLogger, INFO
from datetime import datetime, timedelta
import traceback
from time import perf_counter

from app.database.repos.card import CardRepository
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.deck import DeckRepository
from app.config import settings
from app.services import CardBulkBufferService
from .scheduler import scheduler

logger = getLogger(__name__)
logger.setLevel(INFO)


@scheduler.scheduled_job(
    "interval",
    days=1,
    next_run_time=datetime.now() + timedelta(seconds=10),
    id="animestar.card_users_stats.aggregate_per_second",
    max_instances=1,
)
async def aggregate_card_users_stats():
    repo = CardUsersStatsRepository()
    try:
        logger.info("Aggregating card users stats per second for old records")
        affected = await repo.aggregate_stats_per_second(older_than_days=1)
        logger.info(f"Card users stats aggregation finished, affected rows: {affected}")
    except Exception as e:
        logger.error(f"Error during card users stats aggregation: {e}")
        logger.error(traceback.format_exc())


@scheduler.scheduled_job(
    "interval",
    days=1,
    next_run_time=datetime.now() + timedelta(seconds=10),
    id="animestar.card_decks.delete_empty",
    max_instances=1,
)
async def delete_empty_decks():
    repo = DeckRepository()
    try:
        logger.info("Deleting empty decks")
        affected = await repo.delete_empty_decks()
        logger.info(f"Empty decks deleted, affected rows: {affected}")
    except Exception as e:
        logger.error(f"Error during empty decks deletion: {e}")
        logger.error(traceback.format_exc())


@scheduler.scheduled_job(
    "interval",
    seconds=settings.card_bulk.flush_interval_seconds,
    next_run_time=datetime.now() + timedelta(seconds=2),
    id="animestar.card_bulk.flush_buffer",
    max_instances=1,
)
async def flush_card_bulk_buffer():
    card_repo = CardRepository()
    buffer_service = CardBulkBufferService()
    started_at = perf_counter()
    try:
        result = await buffer_service.flush_into_repo(card_repo)
        if result.candidate_count:
            logger.info(
                "Flushed card bulk buffer: candidates=%s written=%s duration_seconds=%.3f",
                result.candidate_count,
                result.written_count,
                perf_counter() - started_at,
            )
    except Exception as e:
        logger.error(f"Error during card bulk buffer flush: {e}")
        logger.error(traceback.format_exc())
