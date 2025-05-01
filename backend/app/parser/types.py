from pydantic import BaseModel


class PaginatedBase(BaseModel):
    current_page: int
    last_page: int
    total: int | None = None


class Card(BaseModel):
    id: str
    rank: str
    image: str
    name: str
    mp4: str | None = None
    webm: str | None = None
    anime_name: str | None = None
    anime_link: str | None = None
    author: str | None = None


class PaginatedCards(PaginatedBase):
    cards: list[Card]
