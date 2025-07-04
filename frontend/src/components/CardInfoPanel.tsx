import React from 'react';
import { FiExternalLink, FiMaximize2, FiClipboard, FiLayers } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { CardSchema } from '../client';
import { useDomain } from '../context/DomainContext';
import CardStatsDisplay from './CardStatsDisplay';
import '../styles/CardInfoPanel.css';

interface CardInfoPanelProps {
  card: CardSchema | null;
  isOpen: boolean;
  onClose: () => void;
}

const CardInfoRow = ({ 
  label, 
  value, 
  externalLink,
  addComponent 
}: { 
  label: string, 
  value: any,
  externalLink?: string,
  addComponent?: React.ReactNode,
}) => {
  const copyValueToClipboard = () => {
    navigator.clipboard.writeText(value);
  };
  
  return (
    <div className="card-info-row">
      <span className="label">{label}</span>
      <div className="value-container">
        <span className="value">{value}</span>
        <div 
          onClick={copyValueToClipboard}
          className="action-button-arrow"
          title="Copy to clipboard"
        >
          <FiClipboard />
        </div>
        {addComponent}
        {externalLink && (
          <a 
            href={externalLink} 
            target="_blank" 
            rel="noopener noreferrer"
            className="action-button-arrow external-link-red"
            title="Open in Anisite"
          >
            <FiExternalLink />
          </a>
        )}
      </div>
    </div>
  );
};

const CardInfoPanel: React.FC<CardInfoPanelProps> = ({ card, isOpen, onClose }) => {
  const { currentDomain } = useDomain();
  const navigate = useNavigate();

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

  const formatTimeAgo = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    try {
      const now = new Date();
      const date = new Date(dateString);
      const diffInMs = now.getTime() - date.getTime();
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      const diffInDays = Math.floor(diffInHours / 24);
      const diffInWeeks = Math.floor(diffInDays / 7);
      const diffInMonths = Math.floor(diffInDays / 30);
      const diffInYears = Math.floor(diffInDays / 365);

      if (diffInMs < 0) return 'Future date';
      if (diffInHours < 1) {
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
        return diffInMinutes <= 0 ? 'Just now' : `${diffInMinutes}m ago`;
      } else if (diffInHours < 24) {
        return `${diffInHours}h ago`;
      } else if (diffInDays < 7) {
        return `${diffInDays}d ago`;
      } else if (diffInWeeks < 4) {
        return `${diffInWeeks}w ago`;
      } else if (diffInMonths < 12) {
        return `${diffInMonths}mo ago`;
      } else {
        return `${diffInYears}y ago`;
      }
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
          <div className="header-buttons">
            <button 
              className="full-page-button" 
              onClick={() => navigate(`/card/${card.card_id}`)}
              title="Open full page"
            >
              <FiMaximize2 />
            </button>
            <button className="close-button" onClick={onClose}>
              ×
            </button>
          </div>
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
              <CardInfoRow label="Anime Link" value={card.anime_link} addComponent={
                <a
                  href={`/deck/${encodeURIComponent(card.anime_link)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="action-button-arrow deck-button"
                  title="View deck"
                >
                  <FiLayers />
                </a>
              }/>
            )}
            
            {card.created_at && (
              <CardInfoRow label="Created" value={formatTimeAgo(card.created_at)} />
            )}
            
            {card.updated_at && (
              <CardInfoRow label="Updated" value={formatTimeAgo(card.updated_at)} />
            )}

            {/* Card Statistics Display */}
            <CardStatsDisplay cardId={card.card_id} />
          </div>
        </div>
      </div>
    </>
  );
};

export default CardInfoPanel; 