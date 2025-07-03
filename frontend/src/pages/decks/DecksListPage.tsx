import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Configuration, DeckApi, DeckSummarySchema, DeckQuery, DeckFilter } from '../../client';
import '../../styles/Decks.css';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [total, setTotal] = useState(0);
  const [sortBy, setSortBy] = useState<string>('anime_name asc');
  const perPage = 20;

  useEffect(() => {
    if (isAuthenticated) {
      fetchDecks();
    }
  }, [isAuthenticated, page, searchQuery, sortBy]);

  const fetchDecks = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = new Configuration({
        basePath: import.meta.env.VITE_API_URL,
        accessToken: token || undefined
      });
      
      const deckApi = new DeckApi(config);
      
      // Build filter for search query
      let filter: DeckFilter | undefined = undefined;
      if (searchQuery.trim()) {
        filter = {
          anime_name: {
            icontains: searchQuery.trim()
          }
        };
      }

      // Build deck query object
      const deckQuery: DeckQuery = {
        page,
        per_page: perPage,
        filter,
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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handleSortChange = (newSort: string) => {
    setSortBy(newSort);
    setPage(1);
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
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Search anime..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button">
              Search
            </button>
          </div>
        </form>

        <div className="sort-controls">
          <label htmlFor="sort-select">Sort by:</label>
          <select 
            id="sort-select"
            value={sortBy} 
            onChange={(e) => handleSortChange(e.target.value)}
            className="sort-select"
          >
            <option value="anime_name asc">Name A-Z</option>
            <option value="anime_name desc">Name Z-A</option>
            <option value="card_count desc">Most Cards</option>
            <option value="card_count asc">Fewest Cards</option>
          </select>
        </div>
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
                {searchQuery ? 'No decks found matching your search.' : 'No decks available.'}
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