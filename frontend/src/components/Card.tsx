import React from 'react';
import { CardSchema, CardType } from '../client';
import { useDomain } from '../context/DomainContext';

interface CardProps {
  card: CardSchema;
  variant?: 'default' | 'preview';
  className?: string;
  onClick?: () => void;
  canOpenFullPage?: boolean;
}

const Card: React.FC<CardProps> = ({ 
  card, 
  variant = 'default', 
  className = '', 
  onClick,
  canOpenFullPage = true
}) => {
  const { currentDomain } = useDomain();

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getRankClass = (rank: CardType) => {
    return `rank-${rank.toLowerCase()}`;
  };

  const clickHandler = (event: React.MouseEvent<HTMLDivElement>) => {
    if (canOpenFullPage && card.card_id && (event.shiftKey || event.ctrlKey || event.metaKey)) {
      window.open(`/card/${card.card_id}`, '_blank');
    } else {
      onClick?.();
    }
  };

  const baseClass = variant === 'preview' ? 'preview-card' : 'card-item';
  const combinedClassName = `${baseClass} ${getRankClass(card.rank)} ${className}`.trim();

  return (
    <div 
      key={card.id} 
      className={combinedClassName}
      onClick={clickHandler}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="card-content">
        {card.image && !card.mp4 && (
          <div className="card-image">
            <img 
              src={getCardMediaUrl(card.image)} 
              alt={card.name} 
              loading="lazy"
            />
          </div>
        )}
        {card.mp4 && (
          <div className="card-video">
            <video autoPlay loop muted playsInline>
              <source src={getCardMediaUrl(card.mp4)} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}
      </div>
    </div>
  );
};

export default Card; 