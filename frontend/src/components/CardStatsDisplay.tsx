import React, { useState, useEffect, useCallback } from 'react';
import { FiClock } from 'react-icons/fi';
import axios from 'axios';
import { CardCollection } from '../client';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { formatTimeAgo } from '../utils/dateUtils';
import '../styles/CardStatsDisplay.css';

interface CardStatsDisplayProps {
  cardId: number;
  className?: string;
}

type Period = 'day' | 'week' | 'month';

type LastWithPrevItem = {
  id: string;
  card_id: number;
  collection: CardCollection;
  count: number;
  previous_count: number | null;
  delta: number | null;
  created_at: string;
  updated_at: string;
};

const CardStatsDisplay: React.FC<CardStatsDisplayProps> = ({ cardId, className = '' }) => {
  const [items, setItems] = useState<LastWithPrevItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [period, setPeriod] = useState<Period>('day');
  const { isAuthenticated } = useAuth();
  const { t } = useTranslation();

  const fetchLastWithPrev = useCallback(async () => {
    if (!isAuthenticated || !cardId) return;
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      const res = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/card/stats/last-with-prev`,
        { card_id: cardId, period },
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      setItems(res.data?.items || []);
    } catch (err) {
      console.error('Error fetching last-with-prev:', err);
      setError(t('cardStatsDisplay.failedToLoadStats'));
    } finally {
      setLoading(false);
    }
  }, [cardId, isAuthenticated, period, t]);

  useEffect(() => {
    fetchLastWithPrev();
  }, [fetchLastWithPrev]);

  const getCollectionDisplayName = (collection: CardCollection): string => {
    switch (collection) {
      case CardCollection.Trade:
        return t('cardStatsDisplay.trade');
      case CardCollection.Need:
        return t('cardStatsDisplay.need');
      case CardCollection.Owned:
        return t('cardStatsDisplay.owned');
      case CardCollection.UnlockedOwned:
        return t('cardStatsDisplay.unlockedOwned');
      default:
        return collection;
    }
  };

  const getCollectionIcon = (collection: CardCollection): string => {
    switch (collection) {
      case CardCollection.Trade:
        return '🔄';
      case CardCollection.Need:
        return '💎';
      case CardCollection.Owned:
        return '👑';
      case CardCollection.UnlockedOwned:
        return '🔓';
      default:
        return '📊';
    }
  };

  const getFreshnessColor = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 2) return '#4CAF50';
    if (diffInHours < 24) return '#FF9800';
    if (diffInHours < 168) return '#F44336';
    return '#757575';
  };

  const handlePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPeriod(e.target.value as Period);
  };

  if (!isAuthenticated) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        </div>
        <div className="stats-empty">
          {t('cardStatsDisplay.pleaseLogIn')}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        </div>
        <div className="stats-loading">{t('cardStatsDisplay.loadingStatistics')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        </div>
        <div className="stats-error">{error}</div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        </div>
        <div className="stats-empty">{t('cardStatsDisplay.noStatisticsAvailable')}</div>
      </div>
    );
  }

  const periodLabel = period === 'day' ? '24h' : period === 'week' ? '7d' : '30d';

  return (
    <div className={`card-stats-display ${className}`}>
      <div className="card-stats-header">
        <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="period-selector">
            <select value={period} onChange={handlePeriodChange}>
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
            </select>
          </div>
          <div className="freshness-indicator">
            <FiClock size={14} />
            <span>{t('cardStatsDisplay.lastUpdated')}</span>
            <span style={{ color: getFreshnessColor(items[0].updated_at) }}>
              {formatTimeAgo(items[0].updated_at, t)}
            </span>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {items.map((stat) => {
          const delta = stat.delta;
          const deltaClass = delta == null ? 'delta-neutral' : delta > 0 ? 'delta-positive' : delta < 0 ? 'delta-negative' : 'delta-neutral';
          const deltaText = delta == null ? '—' : `${delta > 0 ? '+' : ''}${delta}`;
          return (
            <div key={`${stat.collection}-${stat.id}`} className="stat-item">
              <div className="stat-header">
                <span className="stat-icon">{getCollectionIcon(stat.collection)}</span>
                <span className="stat-label">{getCollectionDisplayName(stat.collection)}</span>
              </div>
              <div className="stat-value">{stat.count}</div>
              <div className="delta-row">
                <span className="delta-period">{periodLabel}</span>
                <span className="delta-prev">Prev: {stat.previous_count ?? '—'}</span>
                <span className={`delta-value ${deltaClass}`}>{deltaText}</span>
              </div>
              <div 
                className="stat-freshness"
                style={{ color: getFreshnessColor(stat.updated_at) }}
              >
                <FiClock size={12} />
                <span>{formatTimeAgo(stat.updated_at, t)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CardStatsDisplay; 