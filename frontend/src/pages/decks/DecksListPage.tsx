import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { DeckApi, DeckSummarySchema, DeckQuery } from '../../client';
import PaginationPage, { PaginationResponse } from '../../components/PaginationPage';
import { deckFilterConfig } from '../../config/deckFilterConfig';
import Card from '../../components/Card';
import '../../styles/Decks.css';
import { createAuthenticatedClient } from '../../utils/apiClient';

interface DecksListPageProps {
  onDeckSelect?: (animeLink: string) => void;
}

const DecksListPage: React.FC<DecksListPageProps> = ({ onDeckSelect }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // API function for fetching decks
  const fetchDecks = async (query: DeckQuery): Promise<PaginationResponse<DeckSummarySchema>> => {
    const deckApi = createAuthenticatedClient(DeckApi);
    const response = await deckApi.getDecksApiDeckPost(query);
    
    return {
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
      items: response.data.items,
      total_pages: response.data.total_pages,
      has_next: response.data.has_next
    };
  };

  // Function to render decks
  const renderDecks = (decks: DeckSummarySchema[]) => (
    <div className="decks-list">
      {decks.map((deck) => (
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
      ))}
    </div>
  );

  const handleDeckClick = (anime_link: string) => {
    if (onDeckSelect) {
      onDeckSelect(anime_link);
    } else {
      // Navigate to the new deck detail route with anime_link as parameter
      const encodedAnimeLink = encodeURIComponent(anime_link);
      navigate(`/deck/${encodedAnimeLink}`);
    }
  };

  // Custom loading component
  const loadingComponent = (
    <div className="loading">Loading decks...</div>
  );

  // Custom error component
  const errorComponent = (error: string) => (
    <div className="error-message">{error}</div>
  );

  // Custom empty component
  const emptyComponent = (
    <div className="no-decks">No decks found matching your criteria.</div>
  );

  // Custom header description
  const headerDescription = (
    <p className="decks-description">
      Browse cards organized by anime series. Each deck contains all cards from a specific anime.
    </p>
  );

  if (!isAuthenticated) {
    return <div className="auth-message">Please log in to view decks.</div>;
  }

  return (
    <div className="decks-container">
      <PaginationPage<DeckSummarySchema, any, DeckQuery>
        fetchData={fetchDecks}
        filterConfig={deckFilterConfig as any}
        renderItems={renderDecks}
        title="Anime Decks"
        perPage={20}
        loadingComponent={loadingComponent}
        errorComponent={errorComponent}
        emptyComponent={emptyComponent}
        headerActions={headerDescription}
        className="decks-pagination-page"
        paginationInfoTemplate={(current, total, itemsCount) => 
          `Page ${current} of ${total} (${itemsCount} total decks)`
        }
      />
    </div>
  );
};

export default DecksListPage; 