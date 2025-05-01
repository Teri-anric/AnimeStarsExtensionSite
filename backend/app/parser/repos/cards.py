from typing import Literal

from ..types import Card, PaginatedCards
from .base import AnimestarBaseRepo


class AnimestarCardsRepo(AnimestarBaseRepo):
    async def get_cards(
        self, page: int = 1, rank: Literal["ass", "s", "a", "b", "c", "d", "e"] = None
    ) -> PaginatedCards:
        """Get cards."""
        CARD_SELECTOR = ".anime-cards--full-page .anime-cards__item"
        TOTAL_SELECTOR = ".tabs__item--active > span"

        params = None
        if rank:
            params = {"rank": rank}

        soup = await self.get_page(f"/cards/page/{page}", params=params)

        total = None
        if _total_selector := soup.select_one(TOTAL_SELECTOR):
            total = _total_selector.text.strip()

        cards = []
        for card in soup.select(CARD_SELECTOR):
            cards.append(
                Card(
                    name=card["data-name"],
                    id=card["data-id"],
                    rank=card["data-rank"].upper(),
                    anime_name=card["data-anime-name"],
                    anime_link=card["data-anime-link"],
                    author=card["data-author"],
                    image=card["data-image"],
                    mp4=card["data-mp4"],
                    webm=card["data-webm"],
                )
            )

        return self.parse_pagination(soup, PaginatedCards, total=total, cards=cards)
