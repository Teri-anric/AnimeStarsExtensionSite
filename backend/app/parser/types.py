from pydantic import BaseModel


class PaginatedBase(BaseModel):
    current_page: int
    last_page: int
    total: int


class Card(BaseModel):
    id: int
    rank: str
    name: str
    author: str | None = None
    anime_name: str | None = None
    anime_link: str | None = None
    image: str | None = None
    mp4: str | None = None
    webm: str | None = None


class PaginatedCards(PaginatedBase):
    cards: list[Card]

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, item: int) -> Card:
        return self.cards[item]

    def __len__(self) -> int:
        return len(self.cards)

    def __contains__(self, item: Card) -> bool:
        return item in self.cards
