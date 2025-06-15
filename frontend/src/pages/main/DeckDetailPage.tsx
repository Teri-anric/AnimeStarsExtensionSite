import { useParams, useNavigate } from 'react-router-dom';
import { DeckDetailPage as DeckDetailComponent } from '../decks';

const DeckDetailPage = () => {
  const { anime_link } = useParams<{ anime_link: string }>();
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/decks');
  };

  if (!anime_link) {
    return <div className="error-message">Invalid deck link</div>;
  }

  // Decode the anime_link since it comes from URL
  const decodedAnimeLink = decodeURIComponent(anime_link);

  return (
    <DeckDetailComponent 
      animeLink={decodedAnimeLink} 
      onBack={handleBack} 
    />
  );
};

export default DeckDetailPage; 