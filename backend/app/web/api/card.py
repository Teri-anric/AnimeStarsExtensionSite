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
                "name": "Naruto",
                "rank": "S",
                "anime_name": "Naruto",
                "anime_link": "https://naruto.com",
                "author": "user",
                "image": "https://naruto.com/image.jpg",
                "mp4": "https://naruto.com/mp4.mp4",
                "webm": "https://naruto.com/webm.webm"
            }
        ]
    }
    """
    values = [card.model_dump() for card in request.cards]
    count = await repo.upsert_bulk(values)
    return CardBulkUpsertResponse(status="ok", count=count)


@router.get("/{card_id}")
async def get_card(card_id: int | UUID, repo: CardRepositoryDep) -> CardSchema:
    card = await repo.get_by_ident(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

