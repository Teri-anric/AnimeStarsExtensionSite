from typing import Literal
from contextlib import suppress

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

        cards = []
        for card in soup.select(CARD_SELECTOR):
            cards.append(
                Card(
                    name=card["data-name"],
                    id=int(card["data-id"]),
                    rank=card["data-rank"].upper(),
                    anime_name=card["data-anime-name"] or None,
                    anime_link=card["data-anime-link"] or None,
                    author=card["data-author"] or None,
                    image=card["data-image"] or None,
                    mp4=card["data-mp4"] or None,
                    webm=card["data-webm"] or None,
                )
            )
        
        total = len(cards)
        with suppress(Exception):
            if _total_selector := soup.select_one(TOTAL_SELECTOR):
                total = int(_total_selector.text.strip().strip("(").strip(")"))

        return self.parse_pagination(soup, PaginatedCards, total=total, cards=cards)
