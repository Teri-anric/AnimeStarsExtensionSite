import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDomain } from '../context/DomainContext';
import { Configuration, DeckApi, DeckSummarySchema, DeckPaginationResponse } from '../client';
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
      console.log('Navigate to deck:', anime_link);
    }
  };

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getRankClass = (rank: string) => {
    return `rank-${rank.toLowerCase()}`;
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
          
          <div className="decks-list">
            {decks.length > 0 ? decks.map((deck) => (
              <div key={deck.anime_link} className="deck-row">
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
                  <button
                    className="view-deck-button"
                    onClick={() => handleDeckClick(deck.anime_link)}
                  >
                    View Full Deck
                  </button>
                </div>
                
                <div className="deck-preview-cards">
                  {deck.preview_cards && deck.preview_cards.length > 0 ? (
                    <div className="preview-cards-grid">
                      {deck.preview_cards.map((card) => (
                        <div key={card.id} className={`preview-card ${getRankClass(card.rank)}`}>
                          {card.image && !card.mp4 && (
                            <div className="card-image">
                              <img 
                                src={getCardMediaUrl(card.image)} 
                                alt={card.name} 
                                loading="lazy"
                              />
                            </div>
                          )}
                          {card.mp4 && (
                            <div className="card-video">
                              <video autoPlay loop muted playsInline>
                                <source src={getCardMediaUrl(card.mp4)} type="video/mp4" />
                                Your browser does not support the video tag.
                              </video>
                            </div>
                          )}

                        </div>
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

export default Decks;