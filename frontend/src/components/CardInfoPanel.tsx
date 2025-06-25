import React from 'react';
import { FiExternalLink } from 'react-icons/fi';
import { CardSchema } from '../client';
import { useDomain } from '../context/DomainContext';
import '../styles/CardInfoPanel.css';

interface CardInfoPanelProps {
  card: CardSchema | null;
  isOpen: boolean;
  onClose: () => void;
}

const CardInfoRow = ({ 
  label, 
  value, 
  externalLink 
}: { 
  label: string, 
  value: any,
  externalLink?: string,
}) => {
  const copyValueToClipboard = () => {
    navigator.clipboard.writeText(value);
  };
  
  return (
    <div className="card-info-row" onClick={copyValueToClipboard}>
      <span className="label">{label}</span>
      <div className="value-container">
        <span className="value">{value}</span>
        {externalLink && <a href={externalLink} target="_blank" rel="noopener noreferrer">
          <FiExternalLink />
        </a>}
      </div>
    </div>
  );
};

const CardInfoPanel: React.FC<CardInfoPanelProps> = ({ card, isOpen, onClose }) => {
  const { currentDomain } = useDomain();

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getAnisiteUrl = (path: string | null, params: object | null = null) => {
    const url = new URL(currentDomain);
    if (path) {
      url.pathname = path;
    }
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value.toString());
      });
    }
    return url.toString();
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
            <CardInfoRow label="ID" value={card.card_id} externalLink={getAnisiteUrl('/cards/users/', { id: card.card_id })}/>

            <CardInfoRow label="External ID" value={card.id} />

            <CardInfoRow 
              label="Author" 
              value={card.author}
              externalLink={getAnisiteUrl('/user/cards/', { name: card.author })}
            />
            
            <CardInfoRow label="Name" value={card.name} />
            
            <CardInfoRow label="Rank" value={card.rank.toUpperCase()} />
            
            {card.anime_name && (
              <CardInfoRow 
                label="Anime" 
                value={card.anime_name}
                externalLink={card.anime_link ? getAnisiteUrl(card.anime_link) : undefined}
              />
            )}
            
            {card.anime_link && (
              <CardInfoRow label="Anime Link" value={card.anime_link} />
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