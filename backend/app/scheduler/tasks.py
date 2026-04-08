from urllib.parse import urlparse
from logging import getLogger, INFO
from datetime import datetime, timedelta
import traceback

from app.parser.exception import AnimestarError
from app.parser.repos.cards import AnimestarCardsRepo
from app.database.repos.card import CardRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.database.repos.card_users_stats import CardUsersStatsRepository
from app.database.repos.deck import DeckRepository
from app.config import settings
from app.services import CardBulkBufferService
from .scheduler import scheduler

logger = getLogger(__name__)
logger.setLevel(INFO)


def url_path(url: str | None) -> str | None:
    if not url:
        return None
    parsed_url = urlparse(url)
    return parsed_url.path


@scheduler.scheduled_job("interval", hours=1, next_run_time=datetime.now() + timedelta(seconds=1), id="animestar.cards.update_cards", max_instances=1)
async def update_cards():
    card_repo = CardRepository()
    user_repo = AnimestarsUserRepo()
    cards_repo = AnimestarCardsRepo()

    try:
        logger.info("Getting cards from animestars.org")
        new_cards = await cards_repo.get_cards(page=1)
        logger.info(f"Retrieved {len(new_cards.cards)} cards")
        
        if not new_cards or not new_cards.cards:
            logger.warning("No cards received from API")
            return False
            
    except AnimestarError as e:
        logger.error(f"AnimestarError: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error getting cards: {e}")
        logger.error(traceback.format_exc())
        return False

    successfully_processed = 0
    for card in new_cards.cards:
        try:
            # update & create user
            user = await user_repo.get_by_username(card.author)
            if not user:
                logger.info(f"Creating user {card.author}")
                await user_repo.create(
                    username=card.author,
                )
            # update & create card
            db_card = await card_repo.get_by_card_id(card.id)
            if db_card:
                logger.info(f"{db_card.id} {db_card}")
                logger.info(f"Updating card {card.id}")
                await card_repo.update(
                    db_card.id,
                    name=card.name,
                    rank=card.rank,
                    author=card.author,
                    anime_name=card.anime_name,
                    image=url_path(card.image),
                    anime_link=url_path(card.anime_link),
                    mp4=url_path(card.mp4),
                    webm=url_path(card.webm),
                )
            else:
                logger.info(f"Creating card {card.id}")
                await card_repo.create(
                    card_id=card.id,
                    name=card.name,
                    rank=card.rank,
                    author=card.author,
                    anime_name=card.anime_name,
                    image=url_path(card.image),
                    anime_link=url_path(card.anime_link),
                    mp4=url_path(card.mp4),
                    webm=url_path(card.webm),
                )
            successfully_processed += 1
        except Exception as e:
            logger.error(f"Error processing card {card.id}: {e}")
            logger.error(traceback.format_exc())
            continue
    
    logger.info(f"Cards update completed. Successfully processed: {successfully_processed}/{len(new_cards.cards)}")
    return True


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
    try:
        result = await buffer_service.flush_into_repo(card_repo)
        if result.candidate_count:
            logger.info(
                "Flushed card bulk buffer: candidates=%s written=%s",
                result.candidate_count,
                result.written_count,
            )
    except Exception as e:
        logger.error(f"Error during card bulk buffer flush: {e}")
        logger.error(traceback.format_exc())
