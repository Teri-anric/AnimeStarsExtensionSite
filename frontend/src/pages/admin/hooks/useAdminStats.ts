import { useCallback, useState } from 'react';
import type { TFunction } from 'i18next';
import type { AdminDatabaseStats } from '../types';

interface UseAdminStatsResult {
  stats: AdminDatabaseStats | null;
  loading: boolean;
  error: string | null;
  fetchStats: () => Promise<void>;
}

export const useAdminStats = (t: TFunction): UseAdminStatsResult => {
  const [stats, setStats] = useState<AdminDatabaseStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/database-stats`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 403) {
        setStats(null);
        setError(t('settings.adminAccessDenied'));
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch admin stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch admin stats:', err);
      setStats(null);
      setError(t('settings.failedToLoadAdminStats'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  return {
    stats,
    loading,
    error,
    fetchStats,
  };
};
