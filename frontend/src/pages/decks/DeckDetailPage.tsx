import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { DeckApi, DeckDetailSchema, CardSchema } from '../../client';
import { useTranslation } from 'react-i18next';
import '../../styles/DeckDetail.css';
import Card from '../../components/Card';
import CardInfoPanel from '../../components/CardInfoPanel';
import { createAuthenticatedClient } from '../../utils/apiClient';

const DeckDetailPage: React.FC = () => {
  const { anime_link } = useParams<{ anime_link: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { t } = useTranslation();
  const [deck, setDeck] = useState<DeckDetailSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Card info panel state
  const [selectedCard, setSelectedCard] = useState<CardSchema | null>(null);
  const [isCardInfoOpen, setIsCardInfoOpen] = useState(false);

  const decodedAnimeLink = anime_link ? decodeURIComponent(anime_link) : '';

  useEffect(() => {
    if (isAuthenticated && decodedAnimeLink) {
      fetchDeckDetail();
    }
  }, [isAuthenticated, decodedAnimeLink]);

  const fetchDeckDetail = async () => {
    try {
      setLoading(true);
      
      const deckApi = createAuthenticatedClient(DeckApi);
      const response = await deckApi.getDeckDetailApiDeckDetailGet(decodedAnimeLink);
      
      setDeck(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching deck details:', err);
      setError(t('decks.failedToFetchDeck'));
      setLoading(false);
    }
  };

  const handleCardClick = (card: CardSchema) => {
    setSelectedCard(card);
    setIsCardInfoOpen(true);
  };

  const handleCardInfoClose = () => {
    setIsCardInfoOpen(false);
    setSelectedCard(null);
  };

  const handleBack = () => {
    navigate('/decks');
  };

  if (!anime_link) {
    return <div className="error-message">{t('decks.invalidDeckLink')}</div>;
  }

  if (!isAuthenticated) {
    return <div className="auth-message">{t('decks.pleaseLogInToViewDeck')}</div>;
  }

  return (
    <div className={`deck-detail-container ${isCardInfoOpen ? 'with-panel' : ''}`}>
      <div className="deck-detail-header">
        <button onClick={handleBack} className="back-button">
          {t('decks.backToDecks')}
        </button>
        
        {loading ? (
          <div className="loading">{t('decks.loadingDeck')}</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : deck ? (
          <>
            <h1 className="deck-title">{deck.anime_name || t('decks.unknownAnime')}</h1>
            <p className="deck-info">
              {deck.cards.length === 1 
                ? t('decks.deckInfo', { cardCount: deck.cards.length, animeLink: deck.anime_link })
                : t('decks.deckInfoPlural', { cardCount: deck.cards.length, animeLink: deck.anime_link })
              }
            </p>
          </>
        ) : null}
      </div>

      {deck && !loading && !error && (
        <div className="cards-grid">
          {deck.cards.map((card) => (
            <Card 
              key={card.id} 
              card={card} 
              onClick={() => handleCardClick(card)}
            />
          ))}
        </div>
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

export default DeckDetailPage; 