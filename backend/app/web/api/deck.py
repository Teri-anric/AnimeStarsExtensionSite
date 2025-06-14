from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, Optional

from app.web.schema.deck import (
    DeckPaginationResponse,
    DeckDetailSchema,
    DeckQuery
)
from app.web.deps import DeckRepositoryDep

router = APIRouter(prefix="/deck", tags=["deck"])


@router.get("/")
async def get_decks(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    query: Annotated[Optional[str], Query()] = None,
    repo: DeckRepositoryDep = None,
) -> DeckPaginationResponse:
    """Get all decks (anime grouped by anime_link) with pagination and optional search"""
    if query:
        result = await repo.search_decks(query, page, per_page)
    else:
        result = await repo.get_all_decks(page, per_page)
    
    return DeckPaginationResponse(**result)


@router.get("/{anime_link}")
async def get_deck_detail(
    anime_link: str,
    repo: DeckRepositoryDep = None,
) -> DeckDetailSchema:
    """Get detailed view of a specific deck with all its cards"""
    deck = await repo.get_deck_by_anime_link(anime_link)
    
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    return DeckDetailSchema(**deck) 