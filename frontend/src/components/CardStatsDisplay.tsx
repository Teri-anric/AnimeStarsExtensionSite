import React, { useState, useEffect } from 'react';
import { FiClock } from 'react-icons/fi';
import { CardUsersStatsSchema, CardStatsApi, CardCollection } from '../client';
import { useAuth } from '../context/AuthContext';
import { createAuthenticatedClient } from '../utils/apiClient';
import { formatTimeAgo } from '../utils/dateUtils';
import '../styles/CardStatsDisplay.css';

interface CardStatsDisplayProps {
  cardId: number;
  className?: string;
}

const CardStatsDisplay: React.FC<CardStatsDisplayProps> = ({ cardId, className = '' }) => {
  const [statsData, setStatsData] = useState<CardUsersStatsSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && cardId) {
      fetchLastStats();
    }
  }, [cardId, isAuthenticated]);

  const fetchLastStats = async () => {
    try {
      setLoading(true);
      setError('');
      const cardStatsApi = createAuthenticatedClient(CardStatsApi);
      
      const response = await cardStatsApi.getLastCardUsersStatsApiCardStatsLastGet(cardId);
      setStatsData(response.data || []);
    } catch (err) {
      console.error('Error fetching last card stats:', err);
      setError('Failed to load card statistics');
    } finally {
      setLoading(false);
    }
  };

  const getCollectionDisplayName = (collection: CardCollection): string => {
    switch (collection) {
      case CardCollection.Trade:
        return 'Trade';
      case CardCollection.Need:
        return 'Need';
      case CardCollection.Owned:
        return 'Owned';
      case CardCollection.UnlockedOwned:
        return 'Unlocked Owned';
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

    if (diffInHours < 2) return '#4CAF50'; // Green - very fresh
    if (diffInHours < 24) return '#FF9800'; // Orange - fresh
    if (diffInHours < 168) return '#F44336'; // Red - old
    return '#757575'; // Gray - very old
  };

  if (!isAuthenticated) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>📊 Card Statistics</h3>
        </div>
        <div className="stats-empty">
          Please log in to view statistics
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>📊 Card Statistics</h3>
        </div>
        <div className="stats-loading">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>📊 Card Statistics</h3>
        </div>
        <div className="stats-error">{error}</div>
      </div>
    );
  }

  if (statsData.length === 0) {
    return (
      <div className={`card-stats-display ${className}`}>
        <div className="card-stats-header">
          <h3>📊 Card Statistics</h3>
        </div>
        <div className="stats-empty">No statistics available</div>
      </div>
    );
  }

  return (
    <div className={`card-stats-display ${className}`}>
      <div className="card-stats-header">
        <h3>📊 Card Statistics</h3>
        <div className="freshness-indicator">
          <FiClock size={14} />
          <span>Last updated</span>
        </div>
      </div>
      
      <div className="stats-grid">
        {statsData.map((stat) => (
          <div key={`${stat.collection}-${stat.id}`} className="stat-item">
            <div className="stat-header">
              <span className="stat-icon">{getCollectionIcon(stat.collection)}</span>
              <span className="stat-label">{getCollectionDisplayName(stat.collection)}</span>
            </div>
            <div className="stat-value">{stat.count}</div>
            <div 
              className="stat-freshness"
              style={{ color: getFreshnessColor(stat.updated_at) }}
            >
              <FiClock size={12} />
              <span>{formatTimeAgo(stat.updated_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CardStatsDisplay; 