import React from 'react';
import { CardSchema, CardType } from '../client';
import { useDomain } from '../context/DomainContext';
import '../styles/CardInfoPanel.css';

interface CardInfoPanelProps {
  card: CardSchema | null;
  isOpen: boolean;
  onClose: () => void;
}

const CardInfoRow = ({ label, value }: { label: string, value: any }) => {
  const copyValueToClipboard = () => {
    navigator.clipboard.writeText(value);
  };
  
  return (
    <div className="card-info-row" onClick={copyValueToClipboard}>
      <span className="label">{label}</span>
      <span className="value">{value}</span>
    </div>
  );
};

const CardInfoPanel: React.FC<CardInfoPanelProps> = ({ card, isOpen, onClose }) => {
  const { currentDomain } = useDomain();

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  if (!card) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`card-info-backdrop ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className={`card-info-panel ${isOpen ? 'open' : ''}`}>
        <div className="card-info-header">
          <h2>Card Details</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="card-info-content">
          {/* Media Section */}
          <div className="card-info-media">
            {card.image && !card.mp4 && (
              <img 
                src={getCardMediaUrl(card.image)} 
                alt={card.name} 
                className="card-info-image"
              />
            )}
            {card.mp4 && (
              <video 
                autoPlay 
                loop 
                muted 
                playsInline
                className="card-info-video"
                controls
              >
                <source src={getCardMediaUrl(card.mp4)} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>

          {/* Info Section */}
          <div className="card-info-details">
            <CardInfoRow label="ID" value={card.card_id} />

            <CardInfoRow label="External ID" value={card.id} />

            <CardInfoRow label="Author" value={card.author} />
            
            <CardInfoRow label="Name" value={card.name} />
            
            <CardInfoRow label="Rank" value={card.rank.toUpperCase()} />
            
            {card.anime_name && (
              <CardInfoRow label="Anime" value={card.anime_name} />
            )}
            
            {card.anime_link && (
              <CardInfoRow label="Anime Link" value={getCardMediaUrl(card.anime_link)} />
            )}
            
            {card.created_at && (
              <CardInfoRow label="Created" value={formatDate(card.created_at)} />
            )}
            
            {card.updated_at && (
              <CardInfoRow label="Updated" value={formatDate(card.updated_at)} />
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default CardInfoPanel; 