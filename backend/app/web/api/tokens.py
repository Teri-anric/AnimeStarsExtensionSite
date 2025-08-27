from __future__ import annotations
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..auth.deps import ProtectedDep
from ...database.types.pagination import Pagination, PaginationQuery
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tokens", tags=["tokens"])  # /api/tokens via parent include


class IndexedToken(BaseModel):
    symbol: str
    name: str | None = None
    mentions_24h: int = 0
    last_seen_at: datetime | None = None


class IndexedTokensResponse(Pagination[IndexedToken]):
    pass


class ParsedContentItem(BaseModel):
    id: str
    source: str  # e.g., telegram:@channel, fourchan:/b/
    source_url: str | None = None
    content: str
    created_at: datetime
    tokens: list[str] = Field(default_factory=list)


class ParsedContentResponse(Pagination[ParsedContentItem]):
    pass


@router.post("/list", response_model=IndexedTokensResponse)
async def list_indexed_tokens(
    _: ProtectedDep,
    query: PaginationQuery,
):
    # Mocked data until real repo exists
    items: list[IndexedToken] = [
        IndexedToken(symbol="BTC", name="Bitcoin", mentions_24h=120, last_seen_at=datetime.utcnow()),
        IndexedToken(symbol="ETH", name="Ethereum", mentions_24h=95, last_seen_at=datetime.utcnow()),
    ]

    page = query.page or 1
    per_page = query.per_page or 10
    start = (page - 1) * per_page
    end = start + per_page
    paged = items[start:end]
    return IndexedTokensResponse(total=len(items), page=page, per_page=per_page, items=paged)


@router.post("/parsed-content", response_model=ParsedContentResponse)
async def list_parsed_content(
    _: ProtectedDep,
    query: PaginationQuery,
    start_date: Annotated[datetime | None, Query(None)] = None,
    end_date: Annotated[datetime | None, Query(None)] = None,
):
    # Mocked data; filter by optional dates
    data: list[ParsedContentItem] = [
        ParsedContentItem(
            id="1",
            source="telegram:@crypto_news",
            source_url="https://t.me/crypto_news/123",
            content="BTC pumping hard. ETH looking strong.",
            created_at=datetime.utcnow(),
            tokens=["BTC", "ETH"],
        ),
        ParsedContentItem(
            id="2",
            source="4chan:/biz/",
            source_url="https://boards.4channel.org/biz/thread/456",
            content="Is SOL the next big thing?",
            created_at=datetime.utcnow(),
            tokens=["SOL"],
        ),
    ]

    def within_range(item: ParsedContentItem) -> bool:
        if start_date and item.created_at < start_date:
            return False
        if end_date and item.created_at > end_date:
            return False
        return True

    filtered = [d for d in data if within_range(d)]
    page = query.page or 1
    per_page = query.per_page or 10
    start = (page - 1) * per_page
    end = start + per_page
    paged = filtered[start:end]
    return ParsedContentResponse(total=len(filtered), page=page, per_page=per_page, items=paged)

