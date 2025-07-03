from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .pagination import PaginationRepository
from ..models.animestars.deck import AnimestarsCardDeck
from ..types.pagination import PaginationQuery, Pagination


class DeckRepository(PaginationRepository[AnimestarsCardDeck]):
    """Repository for managing card decks grouped by anime_link"""

    @property
    def entry_class(self) -> type[AnimestarsCardDeck]:  # type: ignore
        return AnimestarsCardDeck

    async def search(self, query: PaginationQuery) -> Pagination[AnimestarsCardDeck]:
        return await self.paginate(
            select(AnimestarsCardDeck).options(selectinload(AnimestarsCardDeck.cards)),
            query,
        )

    async def get_deck_by_anime_link(
        self, anime_link: str
    ) -> AnimestarsCardDeck | None:
        """Get all cards for a specific anime_link (deck)"""
        return await self.scalar(
            select(AnimestarsCardDeck)
            .where(AnimestarsCardDeck.anime_link == anime_link)
            .options(selectinload(AnimestarsCardDeck.cards))
        )
