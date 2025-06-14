import { useState } from 'react';
import Decks from './Decks';
import DeckDetail from './DeckDetail';

const DecksPage = () => {
  const [selectedDeck, setSelectedDeck] = useState<string | null>(null);

  const handleDeckSelect = (animeLink: string) => {
    setSelectedDeck(animeLink);
  };

  const handleBackToDecks = () => {
    setSelectedDeck(null);
  };

  return (
    <div className="decks-page">
      {selectedDeck ? (
        <DeckDetail 
          animeLink={selectedDeck} 
          onBack={handleBackToDecks} 
        />
      ) : (
        <DecksWithNavigation onDeckSelect={handleDeckSelect} />
      )}
    </div>
  );
};

// Enhanced Decks component with navigation
const DecksWithNavigation = ({ onDeckSelect }: { onDeckSelect: (animeLink: string) => void }) => {
  return <Decks onDeckSelect={onDeckSelect} />;
};

export default DecksPage;