import React from 'react';
import { FiExternalLink, FiMaximize2, FiClipboard, FiLayers } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { CardSchema } from '../client';
import { useDomain } from '../context/DomainContext';
import { useTranslation } from 'react-i18next';
import { formatTimeAgo } from '../utils/dateUtils';
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
  const { t } = useTranslation();
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
          title={t('cardInfoPanel.copyToClipboard')}
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
            title={t('cardInfoPanel.openInAnisite')}
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
  const { t } = useTranslation();

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
          <h2>{t('cardInfoPanel.cardDetails')}</h2>
          <div className="header-buttons">
            <button 
              className="full-page-button" 
              onClick={() => navigate(`/card/${card.card_id}`)}
              title={t('cardInfoPanel.openFullPage')}
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
                {t('cards.videoNotSupported')}
              </video>
            )}
          </div>

          {/* Info Section */}
          <div className="card-info-details">
            <CardInfoRow label={t('cardInfoPanel.id')} value={card.card_id} externalLink={getAnisiteUrl('/cards/users/', { id: card.card_id })}/>

            <CardInfoRow label={t('cardInfoPanel.externalId')} value={card.id} />

            <CardInfoRow 
              label={t('cardInfoPanel.author')} 
              value={card.author}
              externalLink={getAnisiteUrl('/user/cards/', { name: card.author })}
            />
            
            <CardInfoRow label={t('cardInfoPanel.name')} value={card.name} />
            
            <CardInfoRow label={t('cardInfoPanel.rank')} value={card.rank.toUpperCase()} />
            
            {card.anime_name && (
              <CardInfoRow 
                label={t('cardInfoPanel.anime')} 
                value={card.anime_name}
                externalLink={card.anime_link ? getAnisiteUrl(card.anime_link) : undefined}
              />
            )}
            
            {card.anime_link && (
              <CardInfoRow label={t('cardInfoPanel.animeLink')} value={card.anime_link} addComponent={
                <a
                  href={`/deck/${encodeURIComponent(card.anime_link)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="action-button-arrow deck-button"
                  title={t('cardInfoPanel.viewDeck')}
                >
                  <FiLayers />
                </a>
              }/>
            )}
            
            {card.created_at && (
              <CardInfoRow label={t('cardInfoPanel.created')} value={formatTimeAgo(card.created_at)} />
            )}
            
            {card.updated_at && (
              <CardInfoRow label={t('cardInfoPanel.updated')} value={formatTimeAgo(card.updated_at)} />
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
