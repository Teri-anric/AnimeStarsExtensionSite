import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { CardApi, CardSchema, CardFilter, CardQuery } from '../../client';
import '../../styles/Cards.css';
import FilterQuery from '../../components/FilterQuery';
import { cardFilterConfig } from '../../config/cardFilterConfig';
import Card from '../../components/Card';
import CardInfoPanel from '../../components/CardInfoPanel';

const CardsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  const [cards, setCards] = useState<CardSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [perPage] = useState(63);
  
  // Card info panel state
  const [selectedCard, setSelectedCard] = useState<CardSchema | null>(null);
  const [isCardInfoOpen, setIsCardInfoOpen] = useState(false);
  
  // Get values from URL parameters (FilterQuery now handles filter and sort)
  const page = parseInt(searchParams.get('page') || '1');
  const sortBy = searchParams.get('sort') || cardFilterConfig.defaults.sort;
  const filterParam = searchParams.get('filter');
  
  // Parse filter from URL (FilterQuery now handles this, but we need it for API calls)
  const [currentFilter, setCurrentFilter] = useState<CardFilter | null>(() => {
    if (filterParam) {
      try {
        return JSON.parse(filterParam);
      } catch (e) {
        console.error('Failed to parse filter from URL:', e);
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    if (isAuthenticated) {
      setCards([]);
      setLoading(true);
      fetchCards();
    }
  }, [isAuthenticated, page, currentFilter, sortBy]);

  useEffect(() => {
    // Update filter state when URL changes (FilterQuery manages the URL, we just read from it)
    if (filterParam) {
      try {
        const parsedFilter = JSON.parse(filterParam);
        setCurrentFilter(parsedFilter);
      } catch (e) {
        console.error('Failed to parse filter from URL:', e);
        setCurrentFilter(null);
      }
    } else {
      setCurrentFilter(null);
    }
  }, [filterParam]);

  const fetchCards = async () => {
    try {
      const cardApi = createAuthenticatedClient(CardApi);
      
      console.log('Fetching cards with filter:', JSON.stringify(currentFilter, null, 2));
      console.log('Sort by:', sortBy);
      
      const cardQuery: CardQuery = {
        page,
        per_page: perPage,
        filter: currentFilter,
        order_by: sortBy
      };

      const response = await cardApi.getCardsApiCardPost(cardQuery);
      
      console.log('Server response:', {
        total: response.data.total,
        totalPages: response.data.total_pages,
        itemsCount: response.data.items.length,
        firstItem: response.data.items[0]
      });
      
      setCards(response.data.items);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching cards:', err);
      setError('Failed to fetch cards. Please try again later.');
      setLoading(false);
    }
  };

  const updateSearchParams = (updates: Record<string, string | null>) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === '') {
        newParams.delete(key);
      } else {
        newParams.set(key, value);
      }
    });
    
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      updateSearchParams({ page: newPage.toString() });
    }
  };

  const handleFilterChange = (filter: CardFilter | null) => {
    setCurrentFilter(filter);
    // FilterQuery now handles URL updates automatically
    // Reset to first page when filter changes
    updateSearchParams({ page: '1' });
  };

  const handleSortChange = (value: string) => {
    // FilterQuery now handles URL updates automatically
    // Reset to first page when sort changes
    updateSearchParams({ page: '1' });
  };

  const handleSearch = () => {
    // This is called by FilterQuery when search is triggered
    // Reset to first page when searching
    updateSearchParams({ page: '1' });
  };

  const handleCardClick = (card: CardSchema) => {
    setSelectedCard(card);
    setIsCardInfoOpen(true);
  };

  const handleCardInfoClose = () => {
    setIsCardInfoOpen(false);
    setSelectedCard(null);
  };

  if (!isAuthenticated) {
    return <div className="auth-message">Please log in to view cards.</div>;
  }

  return (
    <div className={`cards-container ${isCardInfoOpen ? 'with-panel' : ''}`}>
      <div className="cards-header">
        <h1>Anime Cards</h1>
      </div>

      <div className="cards-controls">
        <FilterQuery
          config={cardFilterConfig}
          filter={currentFilter as any}
          onFilterChange={(filter: any) => handleFilterChange(filter as CardFilter)}
          currentSort={sortBy}
          onSortChange={handleSortChange}
          onSearch={handleSearch}
        />
      </div>

      {loading ? (
        <div className="loading">Loading cards...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="cards-grid">
            {cards.length > 0 ? cards.map((card) => (
              <Card 
                key={card.id} 
                card={card} 
                onClick={() => handleCardClick(card)}
              />
            )) : (
              <div className="no-cards">No cards found matching your criteria.</div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(page - 1)} 
                disabled={page <= 1}
              >
                Previous
              </button>
              
              <span>Page {page} of {totalPages}</span>
              
              <button 
                onClick={() => handlePageChange(page + 1)} 
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
      
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