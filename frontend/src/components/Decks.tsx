import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDomain } from '../context/DomainContext';
import { Configuration, DeckApi, DeckSummarySchema, DeckPaginationResponse, DeckDetailSchema } from '../client';
import '../styles/Decks.css';

interface DecksProps {
  onDeckSelect?: (animeLink: string) => void;
}

const Decks: React.FC<DecksProps> = ({ onDeckSelect }) => {
  const { isAuthenticated } = useAuth();
  const { currentDomain } = useDomain();
  const [decks, setDecks] = useState<DeckSummarySchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [total, setTotal] = useState(0);
  const [expandedDecks, setExpandedDecks] = useState<Set<string>>(new Set());
  const [deckDetails, setDeckDetails] = useState<Map<string, DeckDetailSchema>>(new Map());
  const [loadingDecks, setLoadingDecks] = useState<Set<string>>(new Set());
  const perPage = 20;

  useEffect(() => {
    if (isAuthenticated) {
      fetchDecks();
    }
  }, [isAuthenticated, page, searchQuery]);

  const fetchDecks = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = new Configuration({
        basePath: import.meta.env.VITE_API_URL,
        accessToken: token || undefined
      });
      
      const deckApi = new DeckApi(config);
      const response = await deckApi.getDecksApiDeckGet(
        page,
        perPage,
        searchQuery.trim() || null
      );
      
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

  const handleDeckClick = (anime_link: string) => {
    if (onDeckSelect) {
      onDeckSelect(anime_link);
    } else {
      // Fallback for when used without navigation
      console.log('Navigate to deck:', anime_link);
      alert(`Deck selected: ${anime_link}`);
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

      {loading ? (
        <div className="loading">Loading decks...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="decks-info">
            <p>Total decks: {total}</p>
          </div>
          
          <div className="decks-grid">
            {decks.length > 0 ? decks.map((deck) => (
              <div 
                key={deck.anime_link} 
                className="deck-card"
                onClick={() => handleDeckClick(deck.anime_link)}
              >
                <div className="deck-info">
                  <h3 className="deck-title">
                    {deck.anime_name || 'Unknown Anime'}
                  </h3>
                  <p className="deck-card-count">
                    {deck.card_count} card{deck.card_count !== 1 ? 's' : ''}
                  </p>
                  <div className="deck-link">
                    <small>{deck.anime_link}</small>
                  </div>
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

export default Decks;