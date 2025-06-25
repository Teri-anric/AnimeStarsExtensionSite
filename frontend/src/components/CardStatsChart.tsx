import React, { useEffect, useState, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { 
  CardStatsApi, 
  CardUsersStatsSchema, 
  CardCollection, 
  CardUsersStatsQuery,
  Direction 
} from '../client';
import { createAuthenticatedClient } from '../utils/apiClient';
import { useAuth } from '../context/AuthContext';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface CardStatsChartProps {
  cardId: number;
  className?: string;
}

const CardStatsChart: React.FC<CardStatsChartProps> = ({ cardId, className = '' }) => {
  const [statsData, setStatsData] = useState<CardUsersStatsSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const { isAuthenticated } = useAuth();

  const fetchCardStats = useCallback(async () => {
    if (!isAuthenticated || !cardId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');
      const cardStatsApi = createAuthenticatedClient(CardStatsApi);
      
      // Получаем всю историю статистики для карточки
      const query: CardUsersStatsQuery = {
        filter: {
          card_id: {
            eq: cardId
          }
        },
        order_by: [
          {
            property: 'created_at',
            direction: Direction.Asc
          }
        ],
        per_page: 1000 // Получаем максимум записей
      };
      
      const response = await cardStatsApi.getCardUsersStatsByCardIdApiCardStatsPost(query);
      // API возвращает CardUsersStatsResponse с пагинацией, а не массив напрямую
      setStatsData((response.data as any).items || []);
    } catch (err) {
      console.error('Error fetching card stats:', err);
      setError('Failed to load card statistics');
    } finally {
      setLoading(false);
    }
  }, [cardId, isAuthenticated]);

  useEffect(() => {
    fetchCardStats();
  }, [fetchCardStats]);

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

  const getCollectionColor = (collection: CardCollection): string => {
    switch (collection) {
      case CardCollection.Trade:
        return 'rgba(255, 99, 132, 1)';
      case CardCollection.Need:
        return 'rgba(54, 162, 235, 1)';
      case CardCollection.Owned:
        return 'rgba(75, 192, 192, 1)';
      case CardCollection.UnlockedOwned:
        return 'rgba(153, 102, 255, 1)';
      default:
        return 'rgba(128, 128, 128, 1)';
    }
  };

  const prepareCollectionData = () => {
    // Группируем данные по типу коллекции
    const collectionGroups: Record<CardCollection, CardUsersStatsSchema[]> = {
      [CardCollection.Trade]: [],
      [CardCollection.Need]: [],
      [CardCollection.Owned]: [],
      [CardCollection.UnlockedOwned]: [],
    };

    statsData.forEach(stat => {
      if (collectionGroups[stat.collection]) {
        collectionGroups[stat.collection].push(stat);
      }
    });

    return collectionGroups;
  };

  const createChartData = (data: CardUsersStatsSchema[], collection: CardCollection) => {
    return {
      datasets: [
        {
          label: getCollectionDisplayName(collection),
          data: data.map(stat => ({
            x: new Date(stat.created_at),
            y: stat.count,
          })),
          borderColor: getCollectionColor(collection),
          backgroundColor: getCollectionColor(collection).replace('1)', '0.1)'),
          tension: 0.4,
          fill: false,
          pointBackgroundColor: getCollectionColor(collection),
          pointBorderColor: getCollectionColor(collection),
          pointRadius: 6,
          pointHoverRadius: 8,
        },
      ],
    };
  };

  const chartOptions = (collectionName: string) => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: false, // Скрываем легенду для отдельных графиков
      },
      title: {
        display: true,
        text: `${collectionName} Collection`,
        color: '#ffffff',
        font: {
          size: 14,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        callbacks: {
          title: (context: any[]) => {
            if (context[0]?.parsed?.x) {
              return new Date(context[0].parsed.x).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });
            }
            return '';
          },
          label: (context: any) => {
            return `Count: ${context.parsed.y}`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          displayFormats: {
            hour: 'MMM dd HH:mm',
            day: 'MMM dd',
            week: 'MMM dd',
            month: 'MMM yyyy',
          },
        },
        ticks: {
          color: '#ffffff',
          maxTicksLimit: 6,
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: '#ffffff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  });

  if (loading) {
    return (
      <div className={`card-stats-chart ${className}`}>
        <div className="stats-loading">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card-stats-chart ${className}`}>
        <div className="stats-error">{error}</div>
      </div>
    );
  }

  if (statsData.length === 0) {
    return (
      <div className={`card-stats-chart ${className}`}>
        <div className="stats-no-data">No statistics available for this card</div>
      </div>
    );
  }

  const collectionData = prepareCollectionData();
  const collectionsWithData = Object.entries(collectionData).filter(([_, data]) => data.length > 0);

  return (
    <div className={`card-stats-chart ${className}`}>
      <div className="chart-title">
        <h3>Card Collection Statistics Over Time</h3>
      </div>
      <div className="charts-grid">
        {collectionsWithData.map(([collection, data]) => (
          <div key={collection} className="individual-chart">
            <Line 
              data={createChartData(data, collection as CardCollection)} 
              options={chartOptions(getCollectionDisplayName(collection as CardCollection))} 
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CardStatsChart; 