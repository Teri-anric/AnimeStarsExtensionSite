from fastapi import APIRouter, Query, HTTPException
from typing import Annotated
from uuid import UUID

from app.web.schema.card import (
    CardQuery,
    CardPaginationResponse,
    CardSchema,
    CardUsersSummaryResponse,
    CardUsersSummarySchema,
)
from app.web.deps import CardRepositoryDep, SummaryCardUsersRepositoryDep
from app.database.types.pagination import PaginationQuery
from app.database.enum import CardCollection
from app.filters.metadata import default_metadata_provider

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
    return await repo.search(
        PaginationQuery(
            page=query.page,
            per_page=query.per_page,
            filter=query.filter,
            order_by=query.build_order_by(),
        )
    )


@router.get("/{card_id}")
async def get_card(card_id: int | UUID, repo: CardRepositoryDep) -> CardSchema:
    card = await repo.get_by_ident(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.get("/{card_id}/users/summary")
async def get_card_users_summary(
    card_id: int | UUID,
    repo: SummaryCardUsersRepositoryDep,
) -> CardUsersSummaryResponse:
    return await repo.get_card_users_summary(card_id)


@router.get("/{card_id}/users/summary/{collection}")
async def get_card_users_summary_by_collection(
    card_id: int | UUID,
    collection: CardCollection,
    repo: SummaryCardUsersRepositoryDep,
) -> CardUsersSummarySchema:
    return await repo.get_card_users_summary_by_collection(card_id, collection)
