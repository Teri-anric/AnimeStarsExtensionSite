import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Configuration, DeckApi, DeckSummarySchema, DeckQuery, DeckFilter } from '../../client';
import '../../styles/Decks.css';
import FilterQuery from '../../components/FilterQuery';
import { deckFilterConfig } from '../../config/deckFilterConfig';
import Card from '../../components/Card';

interface DecksListPageProps {
  onDeckSelect?: (animeLink: string) => void;
}

const DecksListPage: React.FC<DecksListPageProps> = ({ onDeckSelect }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [decks, setDecks] = useState<DeckSummarySchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [currentFilter, setCurrentFilter] = useState<DeckFilter | null>(null);
  const [sortBy, setSortBy] = useState<string>(deckFilterConfig.defaults.sort);
  const perPage = 20;

  useEffect(() => {
    if (isAuthenticated) {
      fetchDecks();
    }
  }, [isAuthenticated, page, currentFilter, sortBy]);

  const fetchDecks = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = new Configuration({
        basePath: import.meta.env.VITE_API_URL,
        accessToken: token || undefined
      });
      
      const deckApi = new DeckApi(config);

      // Build deck query object
      const deckQuery: DeckQuery = {
        page,
        per_page: perPage,
        filter: currentFilter,
        order_by: sortBy as any
      };
      
      const response = await deckApi.getDecksApiDeckPost(deckQuery);
      
      setDecks(response.data.items);
      setTotalPages(response.data.total_pages);
      setTotal(response.data.total);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching decks:', err);
      setError('Failed to fetch decks. Please try again later.');
      setLoading(false);
    }
  };

  const handleFilterChange = (filter: DeckFilter | null) => {
    setCurrentFilter(filter);
    setPage(1); // Reset to first page when filter changes
  };

  const handleSortChange = (newSort: string) => {
    setSortBy(newSort);
    setPage(1);
  };

  const handleSearch = () => {
    // This is called by FilterQuery when search is triggered
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handleDeckClick = (anime_link: string) => {
    if (onDeckSelect) {
      onDeckSelect(anime_link);
    } else {
      // Navigate to the new deck detail route with anime_link as parameter
      const encodedAnimeLink = encodeURIComponent(anime_link);
      navigate(`/deck/${encodedAnimeLink}`);
    }
  };

  if (!isAuthenticated) {
    return <div className="auth-message">Please log in to view decks.</div>;
  }

  return (
    <div className="decks-container">
      <div className="decks-header">
        <h1>Anime Decks</h1>
        <p className="decks-description">
          Browse cards organized by anime series. Each deck contains all cards from a specific anime.
        </p>
      </div>

      <div className="decks-controls">
        <FilterQuery
          config={deckFilterConfig}
          filter={currentFilter as any}
          onFilterChange={(filter: any) => handleFilterChange(filter as DeckFilter)}
          currentSort={sortBy}
          onSortChange={handleSortChange}
          onSearch={handleSearch}
        />
      </div>

      {loading ? (
        <div className="loading">Loading decks...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="decks-info">
            <p>Total decks: {total}</p>
          </div>
          
          <div className="decks-list">
            {decks.length > 0 ? decks.map((deck) => (
              <div key={deck.anime_link} className="deck-row" onClick={() => handleDeckClick(deck.anime_link)}>
                <div className="deck-header-section">
                  <div className="deck-info">
                    <h2 className="deck-title">
                      {deck.anime_name || 'Unknown Anime'}
                    </h2>
                    <div className="deck-meta">
                      <span className="deck-card-count">
                        {deck.card_count} card{deck.card_count !== 1 ? 's' : ''}
                      </span>
                      <span className="deck-link">
                        {deck.anime_link}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="deck-preview-cards">
                  {deck.cards && deck.cards.length > 0 ? (
                    <div className="preview-cards-grid">
                      {deck.cards.slice(0, 6).map((card) => (
                        <Card key={card.id} card={card} variant="preview" />
                      ))}
                    </div>
                  ) : (
                    <div className="no-preview-cards">No preview cards available</div>
                  )}
                </div>
              </div>
            )) : (
              <div className="no-decks">
                {currentFilter ? 'No decks found matching your search.' : 'No decks available.'}
              </div>
            )}
          </div>
          
          <div className="pagination">
            <button 
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="pagination-button"
            >
              Previous
            </button>
            
            <span className="pagination-info">
              Page {page} of {totalPages}
            </span>
            
            <button 
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className="pagination-button"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default DecksListPage; 