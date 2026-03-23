from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.web.schema.deck import (
    DeckPaginationResponse,
    DeckDetailSchema,
    DeckQuery,
)
from app.web.deps import DeckRepositoryDep


router = APIRouter(prefix="/deck", tags=["deck"])


@router.post("/")
async def get_decks(
    deck_query: DeckQuery,
    repo: DeckRepositoryDep = None,
) -> DeckPaginationResponse:
    """List decks with pagination, filters and sorting."""
    return await repo.search(deck_query.build())


@router.get("/{deck_id}")
async def get_deck_detail(
    deck_id: UUID,
    repo: DeckRepositoryDep = None,
) -> DeckDetailSchema:
    """Deck detail by internal id (UUID)."""
    deck = await repo.get_deck_by_id(deck_id)

    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")

    return deck
