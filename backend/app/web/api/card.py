from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.web.schema.card import (
    CardQuery,
    CardPaginationResponse,
    CardSchema,
)
from app.web.deps import CardRepositoryDep
from app.web.auth.deps import ProtectedDep


router = APIRouter(prefix="/card", tags=["card"], dependencies=[ProtectedDep])


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


@router.get("/{card_id}")
async def get_card(card_id: int | UUID, repo: CardRepositoryDep) -> CardSchema:
    card = await repo.get_by_ident(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

