import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClipboard, FiExternalLink } from 'react-icons/fi';
import { CardApi, CardSchema } from '../../client';
import { useDomain } from '../../context/DomainContext';
import { useTranslation } from 'react-i18next';
import { formatTimeAgo, formatDateTime } from '../../utils/dateUtils';
import CardStatsChart from '../../components/CardStatsChart';
import '../../styles/CardDetail.css';
import { createAuthenticatedClient } from '../../utils/apiClient';

const CardDetailPage: React.FC = () => {
  const { cardId } = useParams<{ cardId: string }>();
  const navigate = useNavigate();
  const { currentDomain } = useDomain();
  const { t } = useTranslation();
  const [card, setCard] = useState<CardSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


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
      const cardApi = createAuthenticatedClient(CardApi);

      const response = await cardApi.getCardApiCardCardIdGet(parseInt(cardId));
      setCard(response.data);
    } catch (err) {
      console.error('Error fetching card:', err);
      setError(t('cardDetail.failedToLoad'));
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
    
    let url = currentDomain + path;
    
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
        <div className="loading">{t('cardDetail.loadingDetails')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card-detail-container">
        <div className="card-detail-error">
          <p>{error}</p>
          <button onClick={() => navigate(-1)} className="back-button">
            <FiArrowLeft /> {t('common.back')}
          </button>
        </div>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="card-detail-container">
              <div className="card-detail-error">
        <p>{t('cardDetail.cardNotFound')}</p>
        <button onClick={() => navigate(-1)} className="back-button">
          <FiArrowLeft /> {t('common.back')}
        </button>
      </div>
      </div>
    );
  }

  return (
    <div className="card-detail-container">
      <div className="card-detail-header">
        <button onClick={() => navigate(-1)} className="back-button">
          <FiArrowLeft /> {t('common.back')}
        </button>
        <h1>{t('cardDetail.cardDetails')}</h1>
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
                {t('cards.videoNotSupported')}
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
                {t('cards.videoNotSupported')}
              </video>
            )}
          </div>
        </div>

        <div className="card-detail-info">
          <div className="card-detail-main-info">
            <div className="card-info-grid">
              <div className="info-row">
                <strong>{t('cardDetail.cardName')}:</strong>
                <div className="value-with-actions">
                  <span>{card.name}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.name)}
                      className="copy-button"
                      title={t('cardDetail.copyCardName')}
                    >
                      <FiClipboard />
                    </div>
                  </div>
                </div>
              </div>

              <div className="info-row">
                <strong>{t('cardDetail.cardId')}:</strong>
                <div className="value-with-actions">
                  <span>{card.card_id}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.card_id.toString())}
                      className="copy-button"
                      title={t('cardDetail.copyCardId')}
                    >
                      <FiClipboard />
                    </div>
                    <a 
                      href={getAnisiteUrl('/cards/users/', { id: card.card_id })}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="external-link"
                      title={t('cardDetail.viewOnAnisite')}
                    >
                      <FiExternalLink />
                    </a>
                  </div>
                </div>
              </div>

              <div className="info-row">
                <strong>{t('cardDetail.externalId')}:</strong>
                <div className="value-with-actions">
                  <span>{card.id}</span>
                  <div className="action-buttons">
                    <div 
                      onClick={() => copyToClipboard(card.id)}
                      className="copy-button"
                      title={t('cardDetail.copyExternalId')}
                    >
                      <FiClipboard />
                    </div>
                  </div>
                </div>
              </div>

              {card.author && (
                <div className="info-row">
                  <strong>{t('cardDetail.author')}:</strong>
                  <div className="value-with-actions">
                    <span>{card.author}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.author || '')}
                        className="copy-button"
                        title={t('cardDetail.copyAuthor')}
                      >
                        <FiClipboard />
                      </div>
                      <a 
                        href={getAnisiteUrl('/user/cards/', { name: card.author })}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="external-link"
                        title={t('cardDetail.viewAuthorsCards')}
                      >
                        <FiExternalLink />
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {card.anime_name && (
                <div className="info-row">
                  <strong>{t('cardDetail.anime')}:</strong>
                  <div className="value-with-actions">
                    <span>{card.anime_name}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.anime_name || '')}
                        className="copy-button"
                        title={t('cardDetail.copyAnimeName')}
                      >
                        <FiClipboard />
                      </div>
                      {card.anime_link && (
                        <a 
                          href={getAnisiteUrl(card.anime_link)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="external-link"
                          title={t('cardDetail.viewAnime')}
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
                  <strong>{t('cardDetail.animeLink')}:</strong>
                  <div className="value-with-actions">
                    <span>{card.anime_link}</span>
                    <div className="action-buttons">
                      <div 
                        onClick={() => copyToClipboard(card.anime_link || '')}
                        className="copy-button"
                        title={t('cardDetail.copyAnimeLink')}
                      >
                        <FiClipboard />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {card.created_at && (
                <div className="info-row">
                  <strong>{t('cardDetail.created')}:</strong>
                  <div className="value-with-actions">
                    <span>
                      {formatDateTime(card.created_at)}
                      {formatTimeAgo(card.created_at) && (
                        <span style={{ color: 'var(--tt-2)', fontSize: '13px', marginLeft: '8px' }}>
                          ({formatTimeAgo(card.created_at)})
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              )}

              {card.updated_at && (
                <div className="info-row">
                  <strong>{t('cardDetail.updated')}:</strong>
                  <div className="value-with-actions">
                    <span>
                      {formatDateTime(card.updated_at)}
                      {formatTimeAgo(card.updated_at) && (
                        <span style={{ color: 'var(--tt-2)', fontSize: '13px', marginLeft: '8px' }}>
                          ({formatTimeAgo(card.updated_at)})
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
        <h3>{t('cardDetail.cardStatistics')}</h3>
        <CardStatsChart cardId={parseInt(cardId!)} />
      </div>
    </div>
  );
};

export default CardDetailPage; 