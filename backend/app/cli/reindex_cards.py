from app.parser.types import PaginatedCards as CardPaginationResponse
from app.database.repos.card import CardRepository
from app.database.repos.animestars_user import AnimestarsUserRepo
from app.parser.repos.cards import AnimestarCardsRepo
from app.parser.exception import AnimestarError
from app.database.repos.health import HealthRepository
from logging import getLogger, StreamHandler, INFO
import traceback
import asyncio
from urllib.parse import urlparse
import random
from datetime import datetime, UTC

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())

card_repo = CardRepository()
user_repo = AnimestarsUserRepo()
cards_repo = AnimestarCardsRepo()
health_repo = HealthRepository()

def url_path(url: str | None) -> str | None:
    if not url:
        return None
    parsed_url = urlparse(url)
    return parsed_url.path

async def update_cards_by_page(page: int = 1) -> CardPaginationResponse | None:
    try:
        logger.info(f"Getting cards from animestars.org page {page}")
        new_cards = await cards_repo.get_cards(page=page)
        logger.info(f"Retrieved {len(new_cards.cards)} cards")
        
        if not new_cards or not new_cards.cards:
            logger.warning("No cards received from API")
            return None
            
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
    return new_cards


async def reindex_cards():
    page = 1
    start_at = datetime.now(UTC).replace(tzinfo=None)
    while True:
        new_cards = await update_cards_by_page(page)
        if not new_cards:
            await asyncio.sleep(60 + random.randint(0, 60))
            continue
        if new_cards.last_page == page:
            break
        page += 1

    total_cards_count = await health_repo.get_total_cards_count()
    await card_repo.delete_by({"updated_at": {"lt": start_at}})
    total_cards_count_after = await health_repo.get_total_cards_count()
    logger.info(f"Total cards count: {total_cards_count} -> {total_cards_count_after} (deleted: {total_cards_count - total_cards_count_after})")

if __name__ == "__main__":
    asyncio.run(reindex_cards())