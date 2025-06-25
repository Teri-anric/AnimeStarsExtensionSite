import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClipboard, FiExternalLink } from 'react-icons/fi';
import { CardApi, CardSchema } from '../../client';
import { useDomain } from '../../context/DomainContext';
import CardStatsChart from '../../components/CardStatsChart';
import '../../styles/CardDetail.css';

const CardDetailPage: React.FC = () => {
  const { cardId } = useParams<{ cardId: string }>();
  const navigate = useNavigate();
  const { currentDomain } = useDomain();
  const [card, setCard] = useState<CardSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const api = new CardApi();

  useEffect(() => {
    if (cardId) {
      fetchCard();
    }
  }, [cardId]);

  const fetchCard = async () => {
    if (!cardId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.getCardApiCardCardIdGet(parseInt(cardId));
      setCard(response.data);
    } catch (err) {
      console.error('Error fetching card:', err);
      setError('Failed to load card data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getAnisiteUrl = (path: string | null, params: object | null = null) => {
    if (!path) return '';
    
    const baseUrl = 'https://anisite.net';
    let url = baseUrl + path;
    
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
      if (searchParams.toString()) {
        url += '?' + searchParams.toString();
      }
    }
    
    return url;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const getTimeAgo = (dateString: string | null) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
      
      if (diffInSeconds < 60) {
        return `${diffInSeconds}s ago`;
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes}m ago`;
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours}h ago`;
      } else if (diffInSeconds < 2592000) {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days}d ago`;
      } else if (diffInSeconds < 31536000) {
        const months = Math.floor(diffInSeconds / 2592000);
        return `${months}mo ago`;
      } else {
        const years = Math.floor(diffInSeconds / 31536000);
        return `${years}y ago`;
      }
    } catch {
      return '';
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You might want to add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  if (loading) {
    return (
      <div className="card-detail-container">
        <div className="loading">Loading card details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card-detail-container">
        <div className="card-detail-error">
          <p>{error}</p>
          <button onClick={() => navigate(-1)} className="back-button">
            <FiArrowLeft /> Back
          </button>
        </div>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="card-detail-container">
        <div className="card-detail-error">
          <p>Card not found.</p>
          <button onClick={() => navigate(-1)} className="back-button">
            <FiArrowLeft /> Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card-detail-container">
      <div className="card-detail-header">
        <button onClick={() => navigate(-1)} className="back-button">
          <FiArrowLeft /> Back
        </button>
        <h1>Card Details</h1>
      </div>

      <div className="card-detail-content">
        <div className="card-detail-media">
          <div className="card-detail-media-container">
            {card.image && !card.mp4 && (
              <img 
                src={getCardMediaUrl(card.image)} 
                alt={card.name} 
                className="card-detail-image"
              />
            )}
            {card.mp4 && (
              <video 
                autoPlay 
                loop 
                muted 
                playsInline
                controls
                className="card-detail-video"
              >
                <source src={getCardMediaUrl(card.mp4)} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
            {card.webm && !card.mp4 && (
              <video 
                autoPlay 
                loop 
                muted 
                playsInline
                controls
                className="card-detail-video"
              >
                <source src={getCardMediaUrl(card.webm)} type="video/webm" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        </div>

        <div className="card-detail-info">
          <div className="card-detail-main-info">
            <div className="card-info-grid">
              <div className="info-row">
                <strong>Card Name:</strong>
                <div className="value-with-actions">
                  <span>{card.name}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.name)}
                      className="copy-button"
                      title="Copy Card Name"
                    >
                      <FiClipboard />
                    </div>
                  </div>
                </div>
              </div>

              <div className="info-row">
                <strong>Card ID:</strong>
                <div className="value-with-actions">
                  <span>{card.card_id}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.card_id.toString())}
                      className="copy-button"
                      title="Copy Card ID"
                    >
                      <FiClipboard />
                    </div>
                    <a 
                      href={getAnisiteUrl('/cards/users/', { id: card.card_id })}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="external-link"
                      title="View on Anisite"
                    >
                      <FiExternalLink />
                    </a>
                  </div>
                </div>
              </div>

              <div className="info-row">
                <strong>External ID:</strong>
                <div className="value-with-actions">
                  <span>{card.id}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.id)}
                      className="copy-button"
                      title="Copy External ID"
                    >
                      <FiClipboard />
                    </div>
                  </div>
                </div>
              </div>

              {card.author && (
                <div className="info-row">
                  <strong>Author:</strong>
                  <div className="value-with-actions">
                    <span>{card.author}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.author || '')}
                        className="copy-button"
                        title="Copy Author"
                      >
                        <FiClipboard />
                      </div>
                      <a 
                        href={getAnisiteUrl('/user/cards/', { name: card.author })}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="external-link"
                        title="View Author's Cards"
                      >
                        <FiExternalLink />
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {card.anime_name && (
                <div className="info-row">
                  <strong>Anime:</strong>
                  <div className="value-with-actions">
                    <span>{card.anime_name}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.anime_name || '')}
                        className="copy-button"
                        title="Copy Anime Name"
                      >
                        <FiClipboard />
                      </div>
                      {card.anime_link && (
                        <a 
                          href={getAnisiteUrl(card.anime_link)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="external-link"
                          title="View Anime"
                        >
                          <FiExternalLink />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {card.anime_link && (
                <div className="info-row">
                  <strong>Anime Link:</strong>
                  <div className="value-with-actions">
                    <span>{card.anime_link}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.anime_link || '')}
                        className="copy-button"
                        title="Copy Anime Link"
                      >
                        <FiClipboard />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {card.created_at && (
                <div className="info-row">
                  <strong>Created:</strong>
                  <div className="value-with-actions">
                    <span>
                      {formatDate(card.created_at)}
                      {getTimeAgo(card.created_at) && (
                        <span style={{ color: 'var(--tt-2)', fontSize: '13px', marginLeft: '8px' }}>
                          ({getTimeAgo(card.created_at)})
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              )}

              {card.updated_at && (
                <div className="info-row">
                  <strong>Updated:</strong>
                  <div className="value-with-actions">
                    <span>
                      {formatDate(card.updated_at)}
                      {getTimeAgo(card.updated_at) && (
                        <span style={{ color: 'var(--tt-2)', fontSize: '13px', marginLeft: '8px' }}>
                          ({getTimeAgo(card.updated_at)})
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card-stats-section">
        <h3>Card Statistics</h3>
        <CardStatsChart cardId={parseInt(cardId!)} />
      </div>
    </div>
  );
};

export default CardDetailPage; 