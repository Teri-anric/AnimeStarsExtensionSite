import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Configuration, DeckApi, DeckDetailSchema } from '../../client';
import '../../styles/DeckDetail.css';
import Card from '../../components/Card';

const DeckDetailPage: React.FC = () => {
  const { anime_link } = useParams<{ anime_link: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [deck, setDeck] = useState<DeckDetailSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const decodedAnimeLink = anime_link ? decodeURIComponent(anime_link) : '';

  useEffect(() => {
    if (isAuthenticated && decodedAnimeLink) {
      fetchDeckDetail();
    }
  }, [isAuthenticated, decodedAnimeLink]);

  const fetchDeckDetail = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = new Configuration({
        basePath: import.meta.env.VITE_API_URL,
        accessToken: token || undefined
      });
      
      const deckApi = new DeckApi(config);
      const response = await deckApi.getDeckDetailApiDeckDetailGet(decodedAnimeLink);
      
      setDeck(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching deck details:', err);
      setError('Failed to fetch deck details. Please try again later.');
      setLoading(false);
    }
  };



  const handleBack = () => {
    navigate('/decks');
  };

  if (!anime_link) {
    return <div className="error-message">Invalid deck link</div>;
  }

  if (!isAuthenticated) {
    return <div className="auth-message">Please log in to view deck details.</div>;
  }

  return (
    <div className="deck-detail-container">
      <div className="deck-detail-header">
        <button onClick={handleBack} className="back-button">
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
            <Card key={card.id} card={card} />
          ))}
        </div>
      )}
    </div>
  );
};

export default DeckDetailPage; 