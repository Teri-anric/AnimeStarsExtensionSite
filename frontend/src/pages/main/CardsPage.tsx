import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { CardApi, CardSchema, CardQuery } from '../../client';
import PaginationPage, { PaginationResponse } from '../../components/PaginationPage';
import { cardFilterConfig } from '../../config/cardFilterConfig';
import Card from '../../components/Card';
import CardInfoPanel from '../../components/CardInfoPanel';
import '../../styles/Cards.css';

const CardsPage = () => {
  const { isAuthenticated } = useAuth();
  
  // Card info panel state
  const [selectedCard, setSelectedCard] = useState<CardSchema | null>(null);
  const [isCardInfoOpen, setIsCardInfoOpen] = useState(false);

  // API function for fetching cards
  const fetchCards = async (query: CardQuery): Promise<PaginationResponse<CardSchema>> => {
    const cardApi = createAuthenticatedClient(CardApi);
    const response = await cardApi.getCardsApiCardPost(query);
    
    return {
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
      items: response.data.items,
      total_pages: response.data.total_pages,
      has_next: response.data.has_next
    };
  };

  // Function to render cards
  const renderCards = (cards: CardSchema[]) => (
    <div className="cards-grid">
      {cards.map((card) => (
        <Card 
          key={card.id} 
          card={card} 
          onClick={() => handleCardClick(card)}
        />
      ))}
    </div>
  );

  // Card click handler
  const handleCardClick = (card: CardSchema) => {
    setSelectedCard(card);
    setIsCardInfoOpen(true);
  };

  const handleCardInfoClose = () => {
    setIsCardInfoOpen(false);
    setSelectedCard(null);
  };

  // Custom loading component
  const loadingComponent = (
    <div className="loading">Loading cards...</div>
  );

  // Custom error component
  const errorComponent = (error: string) => (
    <div className="error-message">{error}</div>
  );

  // Custom empty component
  const emptyComponent = (
    <div className="no-cards">No cards found matching your criteria.</div>
  );

  if (!isAuthenticated) {
    return <div className="auth-message">Please log in to view cards.</div>;
  }

  return (
    <div className={`cards-container ${isCardInfoOpen ? 'with-panel' : ''}`}>
      <PaginationPage<CardSchema, any, CardQuery>
        fetchData={fetchCards}
        filterConfig={cardFilterConfig as any}
        renderItems={renderCards}
        title="Anime Cards"
        perPage={63}
        loadingComponent={loadingComponent}
        errorComponent={errorComponent}
        emptyComponent={emptyComponent}
        className="cards-pagination-page"
      />
      
      {/* Card Info Panel */}
      <CardInfoPanel
        card={selectedCard}
        isOpen={isCardInfoOpen}
        onClose={handleCardInfoClose}
      />
    </div>
  );
};

export default CardsPage; 