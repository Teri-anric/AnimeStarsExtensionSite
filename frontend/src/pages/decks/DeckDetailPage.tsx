import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DeckApi, DeckDetailSchema, CardSchema } from '../../client';
import { useTranslation } from 'react-i18next';
import '../../styles/DeckDetail.css';
import Card from '../../components/Card';
import CardInfoPanel from '../../components/CardInfoPanel';
import { createAuthenticatedClient } from '../../utils/apiClient';

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isDeckIdParam(value: string | undefined): value is string {
  return Boolean(value && UUID_RE.test(value));
}

const DeckDetailPage: React.FC = () => {
  const { deck_id } = useParams<{ deck_id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [deck, setDeck] = useState<DeckDetailSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [selectedCard, setSelectedCard] = useState<CardSchema | null>(null);
  const [isCardInfoOpen, setIsCardInfoOpen] = useState(false);

  const fetchDeckDetail = useCallback(async () => {
    if (!isDeckIdParam(deck_id)) {
      return;
    }
    try {
      setLoading(true);
      setError('');

      const deckApi = createAuthenticatedClient(DeckApi);
      const response = await deckApi.getDeckDetailApiDeckDeckIdGet(deck_id);

      setDeck(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching deck details:', err);
      setError(t('decks.failedToFetchDeck'));
      setLoading(false);
    }
  }, [deck_id, t]);

  useEffect(() => {
    if (isDeckIdParam(deck_id)) {
      fetchDeckDetail();
    } else {
      setLoading(false);
    }
  }, [deck_id, fetchDeckDetail]);

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

  if (!isDeckIdParam(deck_id)) {
    return <div className="error-message">{t('decks.invalidDeckId')}</div>;
  }

  return (
    <div className={`deck-detail-container ${isCardInfoOpen ? 'with-panel' : ''}`}>
      <div className="deck-detail-header">
        <button type="button" onClick={handleBack} className="back-button">
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
                ? t('decks.deckInfo', {
                    cardCount: deck.cards.length,
                    animeLink: deck.anime_link ?? '',
                  })
                : t('decks.deckInfoPlural', {
                    cardCount: deck.cards.length,
                    animeLink: deck.anime_link ?? '',
                  })}
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

      <CardInfoPanel
        card={selectedCard}
        isOpen={isCardInfoOpen}
        onClose={handleCardInfoClose}
      />
    </div>
  );
};

export default DeckDetailPage;
