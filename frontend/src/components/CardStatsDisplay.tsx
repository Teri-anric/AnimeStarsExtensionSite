import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { FiClock } from 'react-icons/fi';
import { CardUsersStatsSchema, CardStatsApi, CardCollection, CardUsersStatsQuery, Direction } from '../client';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { createAuthenticatedClient } from '../utils/apiClient';
import { formatTimeAgo } from '../utils/dateUtils';
import '../styles/CardStatsDisplay.css';

interface CardStatsDisplayProps {
  cardId: number;
  className?: string;
}

type Period = 'day' | 'week' | 'month';

type CollectionStatsDelta = {
  currentValue: number | null;
  previousValue: number | null;
  delta: number | null;
  deltaPercent: number | null;
  lastUpdated: string | null;
  isMentionSurge: boolean;
  isStrongSignal: boolean; // mentions surge + sentiment change (sentiment optional)
};

const CardStatsDisplay: React.FC<CardStatsDisplayProps> = ({ cardId, className = '' }) => {
  const [statsData, setStatsData] = useState<CardUsersStatsSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [period, setPeriod] = useState<Period>('day');
  const { isAuthenticated } = useAuth();
  const { t } = useTranslation();

  useEffect(() => {
    if (isAuthenticated && cardId) {
      fetchHistoryStats();
    }
  }, [cardId, isAuthenticated]);

  const fetchHistoryStats = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const cardStatsApi = createAuthenticatedClient(CardStatsApi);

      const query: CardUsersStatsQuery = {
        filter: {
          card_id: { eq: cardId }
        },
        order_by: [
          { property: 'created_at', direction: Direction.Asc }
        ],
        per_page: 2000
      };

      const response = await cardStatsApi.getCardUsersStatsByCardIdApiCardStatsPost(query);
      setStatsData((response.data as any).items || []);
    } catch (err) {
      console.error('Error fetching card stats:', err);
      setError(t('cardStatsDisplay.failedToLoadStats'));
    } finally {
      setLoading(false);
    }
  }, [cardId, t, isAuthenticated]);

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

  const getPeriodMs = (p: Period): number => {
    switch (p) {
      case 'day':
        return 24 * 60 * 60 * 1000;
      case 'week':
        return 7 * 24 * 60 * 60 * 1000;
      case 'month':
        return 30 * 24 * 60 * 60 * 1000; // approx
      default:
        return 24 * 60 * 60 * 1000;
    }
  };

  const groupByCollection = useMemo(() => {
    const groups: Record<CardCollection, CardUsersStatsSchema[]> = {
      [CardCollection.Trade]: [],
      [CardCollection.Need]: [],
      [CardCollection.Owned]: [],
      [CardCollection.UnlockedOwned]: [],
    };
    for (const stat of statsData) {
      (groups[stat.collection] ||= []).push(stat);
    }
    return groups;
  }, [statsData]);

  function findLastSnapshotBeforeOrAt(items: CardUsersStatsSchema[], at: Date): CardUsersStatsSchema | undefined {
    if (!items.length) return undefined;
    // items are sorted ASC by created_at
    let left = 0;
    let right = items.length - 1;
    let answer: CardUsersStatsSchema | undefined = undefined;
    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      const midDate = new Date(items[mid].created_at);
      if (midDate.getTime() <= at.getTime()) {
        answer = items[mid];
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }
    return answer;
  }

  function computeDeltaForCollection(items: CardUsersStatsSchema[]): CollectionStatsDelta {
    if (!items.length) {
      return {
        currentValue: null,
        previousValue: null,
        delta: null,
        deltaPercent: null,
        lastUpdated: null,
        isMentionSurge: false,
        isStrongSignal: false,
      };
    }

    const now = new Date();
    const periodMs = getPeriodMs(period);
    const endCurrent = now;
    const startCurrent = new Date(now.getTime() - periodMs);
    const endPrevious = startCurrent;

    const lastPrev = findLastSnapshotBeforeOrAt(items, endPrevious);
    const lastCurr = findLastSnapshotBeforeOrAt(items, endCurrent);

    const previousValue = lastPrev ? lastPrev.count : null;
    const currentValue = lastCurr ? lastCurr.count : previousValue;

    const delta = currentValue != null && previousValue != null ? currentValue - previousValue : null;
    const deltaPercent = delta != null && previousValue && previousValue !== 0 ? (delta / previousValue) * 100 : null;

    const lastUpdated = lastCurr?.updated_at || lastCurr?.created_at || null;

    const MIN_ABS_INCREASE = 10;
    const MIN_PCT_INCREASE = 50; // %
    const isMentionSurge = delta != null && delta > 0 && (delta >= MIN_ABS_INCREASE || (deltaPercent != null && deltaPercent >= MIN_PCT_INCREASE));

    // Sentiment change integration (optional): if sentiment becomes available, set this flag accordingly
    const sentimentChanged = false;

    return {
      currentValue: currentValue ?? null,
      previousValue,
      delta,
      deltaPercent: deltaPercent != null ? deltaPercent : null,
      lastUpdated,
      isMentionSurge,
      isStrongSignal: Boolean(isMentionSurge && sentimentChanged),
    };
  }

  const deltasByCollection = useMemo(() => {
    return {
      [CardCollection.Trade]: computeDeltaForCollection(groupByCollection[CardCollection.Trade]),
      [CardCollection.Need]: computeDeltaForCollection(groupByCollection[CardCollection.Need]),
      [CardCollection.Owned]: computeDeltaForCollection(groupByCollection[CardCollection.Owned]),
      [CardCollection.UnlockedOwned]: computeDeltaForCollection(groupByCollection[CardCollection.UnlockedOwned]),
    } as Record<CardCollection, CollectionStatsDelta>;
  }, [groupByCollection, period]);

  const handlePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as Period;
    setPeriod(value);
  };

  const latestUpdatedAtOverall = useMemo(() => {
    const latest = statsData.reduce<string | null>((acc, curr) => {
      const t = curr.updated_at || curr.created_at;
      if (!acc) return t;
      return new Date(t) > new Date(acc) ? t : acc;
    }, null);
    return latest;
  }, [statsData]);

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

  if (statsData.length === 0) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>{t('cardStatsDisplay.cardStatistics')}</h3>
        </div>
        <div className="stats-empty">{t('cardStatsDisplay.noStatisticsAvailable')}</div>
      </div>
    );
  }

  const periodLabel = ((): string => {
    switch (period) {
      case 'day':
        return '24h';
      case 'week':
        return '7d';
      case 'month':
        return '30d';
      default:
        return '';
    }
  })();

  const collections: CardCollection[] = [
    CardCollection.Trade,
    CardCollection.Need,
    CardCollection.Owned,
    CardCollection.UnlockedOwned,
  ];

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
            {latestUpdatedAtOverall && (
              <span style={{ color: getFreshnessColor(latestUpdatedAtOverall) }}>
                {formatTimeAgo(latestUpdatedAtOverall, t)}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {collections.map((collection) => {
          const delta = deltasByCollection[collection];
          const deltaClass = delta.delta == null
            ? 'delta-neutral'
            : delta.delta > 0
              ? 'delta-positive'
              : delta.delta < 0
                ? 'delta-negative'
                : 'delta-neutral';

          const deltaText = delta.delta == null
            ? '—'
            : `${delta.delta > 0 ? '+' : ''}${delta.delta}`;

          const pctText = delta.deltaPercent == null
            ? ''
            : ` (${delta.deltaPercent > 0 ? '+' : ''}${delta.deltaPercent.toFixed(1)}%)`;

          const cardClasses = [
            'stat-item',
            delta.isStrongSignal ? 'strong-signal' : '',
            !delta.isStrongSignal && delta.isMentionSurge ? 'mentions-surge' : '',
          ].filter(Boolean).join(' ');

          return (
            <div key={collection} className={cardClasses}>
              <div className="stat-header">
                <span className="stat-icon">{getCollectionIcon(collection)}</span>
                <span className="stat-label">{getCollectionDisplayName(collection)}</span>
              </div>
              <div className="stat-value">{delta.currentValue ?? '—'}</div>
              <div className="delta-row">
                <span className="delta-period">{periodLabel}</span>
                <span className="delta-prev">Prev: {delta.previousValue ?? '—'}</span>
                <span className={`delta-value ${deltaClass}`}>{deltaText}{pctText}</span>
              </div>
              {delta.lastUpdated && (
                <div 
                  className="stat-freshness"
                  style={{ color: getFreshnessColor(delta.lastUpdated) }}
                >
                  <FiClock size={12} />
                  <span>{formatTimeAgo(delta.lastUpdated, t)}</span>
                </div>
              )}
              {delta.isStrongSignal && (
                <div className="signal-badge strong">Strong signal</div>
              )}
              {!delta.isStrongSignal && delta.isMentionSurge && (
                <div className="signal-badge surge">Mentions surge</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CardStatsDisplay; 