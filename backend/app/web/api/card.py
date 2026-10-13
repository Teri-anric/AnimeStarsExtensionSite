from fastapi import APIRouter, HTTPException
from uuid import UUID
import logging

from app.web.schema.card import (
    CardQuery,
    CardPaginationResponse,
    CardSchema,
    CardBulkUpsertRequest,
    CardBulkUpsertResponse,
    CardDeckSnapshotRequest,
    CardUpsertSchema,
)
from app.web.deps import CardRepositoryDep, CardBulkBufferServiceDep
from app.util.media_path import normalize_media_path
from app.services.card_ingest_policy import (
    MAX_INGESTED_CARD_ID,
    is_card_id_ingestible,
)

router = APIRouter(prefix="/card", tags=["card"])
logger = logging.getLogger(__name__)

_URL_FIELDS = ("image", "mp4", "webm", "anime_link")



def strip_host_from_url_fields(card: dict) -> dict:
    for field in _URL_FIELDS:
        if field in card:
            card[field] = normalize_media_path(card[field])
    return card


def clear_cards_data_without_stars(cards: list[dict]):
    for card in cards:
        if card.get("image") is None:
            yield card
            continue
        image = card.get("image") or ""
        if "_stars_" in image:
            continue
        yield card


def filter_cards_by_id(cards: list[CardUpsertSchema]) -> list[CardUpsertSchema]:
    accepted = [card for card in cards if is_card_id_ingestible(card.card_id)]
    skipped_count = len(cards) - len(accepted)
    if skipped_count:
        logger.warning(
            "Ignoring %s card payloads with card_id above %s",
            skipped_count,
            MAX_INGESTED_CARD_ID,
        )
    return accepted


async def _write_cards_directly(
    repo,
    cards: list,
) -> int:
    full_upsert_values: list[dict] = []
    partial_update_values: list[dict] = []

    for card in filter_cards_by_id(cards):
        data = strip_host_from_url_fields(card.model_dump(exclude_none=True))
        # Separate cards that have enough data to be fully upserted
        # from those that should only partially update existing records.
        if "name" in data and "rank" in data:
            full_upsert_values.append(data)
        else:
            partial_update_values.append(data)

    total_count = 0
    full_upsert_values = list(clear_cards_data_without_stars(full_upsert_values))
    partial_update_values = list(clear_cards_data_without_stars(partial_update_values))

    if full_upsert_values:
        total_count += await repo.upsert_bulk(full_upsert_values)

    if partial_update_values:
        total_count += await repo.partial_update_by_card_id_bulk(partial_update_values)

    return total_count


@router.post("/")
async def get_cards(
    query: CardQuery,
    repo: CardRepositoryDep,
) -> CardPaginationResponse:
    """
    Get cards with filtering support.
    
    The new filter system supports:
    - All standard fields: id, card_id, name, rank, anime_name, anime_link, author, image, mp4, webm
    - Computed fields: author_username (demonstrates custom logic)
    
    Example filter usage:
    {
        "filter": {
            "name": {"contains": "Naruto"},
            "author_username": {"icontains": "user"},
            "rank": {"eq": "S"}
        }
    }
    """
    return await repo.search(query.build())


@router.post("/bulk")
async def bulk_upsert_cards(
    request: CardBulkUpsertRequest,
    repo: CardRepositoryDep,
    buffer_service: CardBulkBufferServiceDep,
) -> CardBulkUpsertResponse:
    """
    Bulk upsert cards.

    Example request:
    {
        "cards": [
            {
                "card_id": 1,
                "image": "https://naruto.com/image.jpg",
                "anime_link": "https://naruto.com",
            }
        ]
    }
    """
    accepted_cards = filter_cards_by_id(request.cards)
    normalized_cards: list[dict] = []
    for card in accepted_cards:
        data = strip_host_from_url_fields(card.model_dump(exclude_none=True))
        normalized_cards.append(data)
    normalized_cards = list(clear_cards_data_without_stars(normalized_cards))
    if not normalized_cards:
        return CardBulkUpsertResponse(status="ok", count=0)

    try:
        accepted = await buffer_service.enqueue_cards(normalized_cards)
        return CardBulkUpsertResponse(status="ok", count=accepted)
    except Exception as exc:
        if not buffer_service.is_redis_error(exc):
            raise
        logger.exception("Redis is unavailable for /card/bulk, using direct DB fallback")
        total_count = await _write_cards_directly(repo, accepted_cards)
        return CardBulkUpsertResponse(status="ok", count=total_count)


@router.post("/{card_id}/report-deleted-card", status_code=204)
async def report_deleted_card(card_id: int | UUID, repo: CardRepositoryDep) -> None:
    """
    Report that the card no longer exists at the source; removes it from our database.
    """
    deleted = await repo.delete_by_ident(card_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Card not found")


@router.post("/bulk/deck-sync")
async def sync_deck_snapshot(
    request: CardDeckSnapshotRequest,
    repo: CardRepositoryDep,
    buffer_service: CardBulkBufferServiceDep,
) -> CardBulkUpsertResponse:
    accepted_cards = filter_cards_by_id(request.cards)
    normalized_cards = [
        strip_host_from_url_fields(card.model_dump(exclude_none=True))
        for card in accepted_cards
    ]
    if not normalized_cards:
        return CardBulkUpsertResponse(status="ok", count=0)
    existing_ids = await repo.get_card_ids_by_deck_anime_id(request.anime_id)
    snapshot_ids = {card["card_id"] for card in normalized_cards}
    deleted_cards = [
        {"card_id": card_id, "deleted": True}
        for card_id in existing_ids - snapshot_ids
        if is_card_id_ingestible(card_id)
    ]
    accepted = await buffer_service.enqueue_cards(normalized_cards + deleted_cards)
    return CardBulkUpsertResponse(status="ok", count=accepted)


@router.get("/{card_id}")
async def get_card(card_id: int | UUID, repo: CardRepositoryDep) -> CardSchema:
    card = await repo.get_by_ident(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
