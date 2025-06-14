import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDomain } from '../context/DomainContext';
import { Configuration, DeckApi, DeckDetailSchema } from '../client';
import '../styles/DeckDetail.css';

interface DeckDetailProps {
  animeLink: string;
  onBack: () => void;
}

const DeckDetail: React.FC<DeckDetailProps> = ({ animeLink, onBack }) => {
  const { isAuthenticated } = useAuth();
  const { currentDomain } = useDomain();
  const [deck, setDeck] = useState<DeckDetailSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated && animeLink) {
      fetchDeckDetail();
    }
  }, [isAuthenticated, animeLink]);

  const fetchDeckDetail = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = new Configuration({
        basePath: import.meta.env.VITE_API_URL,
        accessToken: token || undefined
      });
      
      const deckApi = new DeckApi(config);
      const response = await deckApi.getDeckDetailApiDeckAnimeLinkGet(animeLink);
      
      setDeck(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching deck details:', err);
      setError('Failed to fetch deck details. Please try again later.');
      setLoading(false);
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
    return <div className="auth-message">Please log in to view deck details.</div>;
  }

  return (
    <div className="deck-detail-container">
      <div className="deck-detail-header">
        <button onClick={onBack} className="back-button">
          ← Back to Decks
        </button>
        
        {loading ? (
          <div className="loading">Loading deck...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : deck ? (
          <>
            <h1 className="deck-title">{deck.anime_name || 'Unknown Anime'}</h1>
            <p className="deck-info">
              {deck.cards.length} card{deck.cards.length !== 1 ? 's' : ''} • {deck.anime_link}
            </p>
          </>
        ) : null}
      </div>

      {deck && !loading && !error && (
        <div className="cards-grid">
          {deck.cards.map((card) => (
            <div key={card.id} className={`card-item ${getRankClass(card.rank)}`}>
              <div className="card-content">
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
                <div className="card-info">
                  <h3 className="card-name">{card.name}</h3>
                  <p className="card-id">#{card.card_id}</p>
                  <p className="card-rank">{card.rank}</p>
                  {card.author && <p className="card-author">By: {card.author}</p>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DeckDetail;