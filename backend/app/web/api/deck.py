from fastapi import APIRouter, HTTPException, Query
from typing import Annotated

from app.web.schema.deck import (
    DeckPaginationResponse,
    DeckDetailSchema,
    DeckQuery
)
from app.web.deps import DeckRepositoryDep
from app.web.auth.deps import ProtectedDep


router = APIRouter(prefix="/deck", tags=["deck"], dependencies=[ProtectedDep])


@router.post("/")
async def get_decks(
    deck_query: DeckQuery,
    repo: DeckRepositoryDep = None,
) -> DeckPaginationResponse:
    """Get all decks (anime grouped by anime_link) with pagination, search and sorting"""
    return await repo.search(deck_query.build())


@router.get("/detail")
async def get_deck_detail(
    anime_link: Annotated[str, Query()],
    repo: DeckRepositoryDep = None,
) -> DeckDetailSchema:
    """Get detailed view of a specific deck with all its cards"""
    deck = await repo.get_deck_by_anime_link(anime_link)
    
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    return deck