from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.web.schema.card import (
    CardQuery,
    CardPaginationResponse,
    CardSchema,
    CardBulkUpsertRequest,
    CardBulkUpsertResponse,
)
from app.web.deps import CardRepositoryDep


router = APIRouter(prefix="/card", tags=["card"])


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
    full_upsert_values: list[dict] = []
    partial_update_values: list[dict] = []

    for card in request.cards:
        data = card.model_dump(exclude_none=True)
        # Separate cards that have enough data to be fully upserted
        # from those that should only partially update existing records.
        if "name" in data and "rank" in data:
            full_upsert_values.append(data)
        else:
            partial_update_values.append(data)

    total_count = 0

    if full_upsert_values:
        total_count += await repo.upsert_bulk(full_upsert_values)

    if partial_update_values:
        total_count += await repo.partial_update_by_card_id_bulk(partial_update_values)

    return CardBulkUpsertResponse(status="ok", count=total_count)


@router.post("/{card_id}/report-deleted-card", status_code=204)
async def report_deleted_card(card_id: int | UUID, repo: CardRepositoryDep) -> None:
    """
    Report that the card no longer exists at the source; removes it from our database.
    """
    deleted = await repo.delete_by_ident(card_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Card not found")


@router.get("/{card_id}")
async def get_card(card_id: int | UUID, repo: CardRepositoryDep) -> CardSchema:
    card = await repo.get_by_ident(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

