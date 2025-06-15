from sqlalchemy import select, func, distinct

from .base import BaseRepository
from ..models.animestars.card import Card
from ..types.deck import DeckSummaryDTO, DeckPaginationDTO, DeckDetailDTO


class DeckRepository(BaseRepository):
    """Repository for managing card decks grouped by anime_link"""
    
    async def get_all_decks(self, page: int = 1, per_page: int = 20) -> DeckPaginationDTO:
        """Get all decks (unique anime_link with card counts) with first 6 cards"""
        offset = (page - 1) * per_page
        
        # Get unique anime_links with card counts
        stmt = (
            select(
                Card.anime_link,
                Card.anime_name,
                func.count(Card.id).label('card_count')
            )
            .where(Card.anime_link.isnot(None))
            .group_by(Card.anime_link, Card.anime_name)
            .order_by(Card.anime_name)
            .offset(offset)
            .limit(per_page)
        )
        
        result = await self.session.execute(stmt)
        decks = result.fetchall()
        
        # Get total count for pagination
        count_stmt = (
            select(func.count(distinct(Card.anime_link)))
            .where(Card.anime_link.isnot(None))
        )
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Get first 6 cards for each deck
        deck_items = []
        for deck in decks:
            # Get first 6 cards for this deck
            cards_stmt = (
                select(Card)
                .where(Card.anime_link == deck.anime_link)
                .order_by(Card.card_id)
                .limit(6)
            )
            cards_result = await self.session.execute(cards_stmt)
            preview_cards = cards_result.scalars().all()
            
            deck_items.append(DeckSummaryDTO(
                anime_link=deck.anime_link,
                anime_name=deck.anime_name,
                card_count=deck.card_count,
                preview_cards=preview_cards
            ))
        
        total_pages = (total + per_page - 1) // per_page
        return DeckPaginationDTO(
            items=deck_items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages
        )
    
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
    
    async def search_decks(self, query: str, page: int = 1, per_page: int = 20) -> DeckPaginationDTO:
        """Search decks by anime name with first 6 cards"""
        offset = (page - 1) * per_page
        
        stmt = (
            select(
                Card.anime_link,
                Card.anime_name,
                func.count(Card.id).label('card_count')
            )
            .where(
                Card.anime_link.isnot(None),
                Card.anime_name.ilike(f'%{query}%')
            )
            .group_by(Card.anime_link, Card.anime_name)
            .order_by(Card.anime_name)
            .offset(offset)
            .limit(per_page)
        )
        
        result = await self.session.execute(stmt)
        decks = result.fetchall()
        
        # Get total count for pagination
        count_stmt = (
            select(func.count(distinct(Card.anime_link)))
            .where(
                Card.anime_link.isnot(None),
                Card.anime_name.ilike(f'%{query}%')
            )
        )
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Get first 6 cards for each deck
        deck_items = []
        for deck in decks:
            # Get first 6 cards for this deck
            cards_stmt = (
                select(Card)
                .where(Card.anime_link == deck.anime_link)
                .order_by(Card.card_id)
                .limit(6)
            )
            cards_result = await self.session.execute(cards_stmt)
            preview_cards = cards_result.scalars().all()
            
            deck_items.append(DeckSummaryDTO(
                anime_link=deck.anime_link,
                anime_name=deck.anime_name,
                card_count=deck.card_count,
                preview_cards=preview_cards
            ))
        
        total_pages = (total + per_page - 1) // per_page
        return DeckPaginationDTO(
            items=deck_items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages
        ) 