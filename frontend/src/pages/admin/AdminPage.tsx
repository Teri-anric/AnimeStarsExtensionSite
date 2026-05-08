import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { formatNumber } from '../../utils/formatUtils';

interface AdminDatabaseStats {
  total_cards: number;
  total_users: number;
  cards_with_stats: number;
  cards_stats_today: number;
}

const AdminPage = () => {
  const { t } = useTranslation();
  const { isAuthenticated, loading: authLoading, isAdmin } = useAuth();
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

  if (authLoading) {
    return <div className="loading">{t('settings.loadingAdminStats')}</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="settings-section">
        <h2>{t('settings.adminPanel')}</h2>
        <p className="setting-description">{t('auth.pleaseLogIn')}</p>
        <Link to="/login" className="button button-secondary">
          {t('auth.login')}
        </Link>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="settings-section">
        <h2>{t('settings.adminPanel')}</h2>
        <p className="setting-description">{t('settings.adminAccessDenied')}</p>
      </div>
    );
  }

  return (
    <div className="settings-section">
      <h2>{t('settings.adminPanel')}</h2>
      <p className="setting-description">{t('settings.adminPanelDescription')}</p>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">{t('settings.loadingAdminStats')}</div>
      ) : (
        <>
          <div className="setting-item">
            <label>{t('settings.totalCards')}</label>
            <div className="setting-value">{formatNumber(stats?.total_cards ?? 0)}</div>
          </div>
          <div className="setting-item">
            <label>{t('settings.totalUsers')}</label>
            <div className="setting-value">{formatNumber(stats?.total_users ?? 0)}</div>
          </div>
          <div className="setting-item">
            <label>{t('settings.cardsWithStats')}</label>
            <div className="setting-value">{formatNumber(stats?.cards_with_stats ?? 0)}</div>
          </div>
          <div className="setting-item">
            <label>{t('settings.statsToday')}</label>
            <div className="setting-value">{formatNumber(stats?.cards_stats_today ?? 0)}</div>
          </div>
        </>
      )}

      <div className="settings-actions">
        <button onClick={fetchStats} className="button button-secondary" disabled={loading}>
          {t('settings.refreshAdminStats')}
        </button>
      </div>
    </div>
  );
};

export default AdminPage;
