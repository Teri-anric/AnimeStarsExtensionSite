from sqlalchemy import select, func

from .pagination import PaginationRepository
from ..models.animestars.card import Card
from ..types.deck import DeckSummaryDTO, DeckDetailDTO
from ..types.pagination import PaginationQuery, Pagination
from app.database.utils import model_to_json


class DeckRepository(PaginationRepository[Card]):
    """Repository for managing card decks grouped by anime_link"""
    
    @property
    def entry_class(self) -> type[Card]:
        return Card
    
    async def search(self, query: PaginationQuery) -> Pagination[DeckSummaryDTO]:
        stmt = (
            select(
                Card.anime_link.label('anime_link'),
                Card.anime_name.label('anime_name'),
                func.count(Card.id).label('card_count'),
                func.array_agg(model_to_json(Card)).label('preview_cards')
            )
            .where(Card.anime_link.isnot(None))
            .group_by(Card.anime_link, Card.anime_name)
        )
        total_stmt = select(func.count(Card.anime_link)).where(Card.anime_link.isnot(None)).group_by(Card.anime_link, Card.anime_name)
        page = await self.paginate(stmt, query, total_base_stmt=total_stmt, is_dto=True)
        deck_items = []
        for deck in page.items:
            deck_items.append(DeckSummaryDTO(
                anime_link=deck.anime_link,
                anime_name=deck.anime_name,
                card_count=deck.card_count,
                preview_cards=deck.preview_cards
            ))
        page.items = deck_items
        return page
    
    
    async def get_deck_by_anime_link(self, anime_link: str) -> DeckDetailDTO | None:
        """Get all cards for a specific anime_link (deck)"""
        stmt = (
            select(Card)
            .where(Card.anime_link == anime_link)
            .order_by(Card.card_id)
        )
        
        result = await self.session.execute(stmt)
        cards = result.scalars().all()
        
        if not cards:
            return None
            
        return DeckDetailDTO(
            anime_link=anime_link,
            anime_name=cards[0].anime_name,
            cards=cards
        )
