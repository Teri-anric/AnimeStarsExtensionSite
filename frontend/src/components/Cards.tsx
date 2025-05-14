import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { createAuthenticatedClient } from '../utils/apiClient';
import { CardApi, CardSchema, CardType } from '../client';
import '../styles/Cards.css';
import { useDomain } from '../context/DomainContext';

const Cards = () => {
  const { isAuthenticated } = useAuth();
  const { currentDomain } = useDomain();
  const [cards, setCards] = useState<CardSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [perPage, setPerPage] = useState(60);
  
  // Filter states
  const [nameFilter, setNameFilter] = useState('');
  const [animeNameFilter, setAnimeNameFilter] = useState('');
  const [rankFilter, setRankFilter] = useState<string>('');

  useEffect(() => {
    if (isAuthenticated) {
      setCards([]);
      setLoading(true);
      fetchCards();
    }
  }, [isAuthenticated, page, perPage, nameFilter, animeNameFilter, rankFilter]);

  const fetchCards = async () => {
    try {
      const cardApi = createAuthenticatedClient(CardApi);
      
      const response = await cardApi.getCardsApiCardGet(
        undefined, // id
        undefined, // cardId
        nameFilter || undefined,
        rankFilter as CardType || undefined,
        animeNameFilter || undefined,
        undefined, // animeLink
        undefined, // author
        undefined, // image
        undefined, // mp4
        undefined, // webm
        page,
        perPage
      );
      
      setCards(response.data.items);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching cards:', err);
      setError('Failed to fetch cards. Please try again later.');
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

  const handleRankChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRankFilter(e.target.value);
    setPage(1);
  };

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getRankClass = (rank: CardType) => {
    return `rank-${rank.toLowerCase()}`;
  };

  return (
    <div className="cards-container">
      <div className="cards-header">
        <h1>Anime Cards</h1>
      
        <div className="filters-container">
          <form onSubmit={handleSearch} className="compact-form">
            <input
              type="text"
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
              placeholder="Card name"
              className="compact-input"
            />
            
            <input
              type="text"
              value={animeNameFilter}
              onChange={(e) => setAnimeNameFilter(e.target.value)}
              placeholder="Anime"
              className="compact-input"
            />
            
            <select
              value={rankFilter}
              onChange={handleRankChange}
              className="compact-select"
            >
              <option value="">All Ranks</option>
              <option value="ass">ASS</option>
              <option value="s">S</option>
              <option value="a">A</option>
              <option value="b">B</option>
              <option value="c">C</option>
              <option value="d">D</option>
              <option value="e">E</option>
            </select>
            
            <button type="submit" className="search-button">Search</button>
          </form>
        </div>
      </div>
      
      {loading ? (
        <div className="loading">Loading cards...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="cards-grid">
            {cards.length > 0 ? cards.map((card) => (
              <div key={card.id} className={`card-item ${getRankClass(card.rank)}`}>
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
                      {/* {card.webm && <source src={getCardMediaUrl(card.webm)} type="video/webm" />} */}
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}
              </div>
            )) : (
              <div className="no-cards">No cards found</div>
            )}
          </div>
          
          <div className="pagination">
            <button 
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
            >
              Previous
            </button>
            
            <span>
              Page {page} of {totalPages}
            </span>
            
            <button 
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Cards; 