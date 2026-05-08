import { useTranslation } from 'react-i18next';
import { formatNumber } from '../../../utils/formatUtils';
import type { AdminDatabaseStats } from '../types';

interface AdminOverviewTabProps {
  error: string | null;
  loading: boolean;
  stats: AdminDatabaseStats | null;
  onRefresh: () => Promise<void>;
}

const AdminOverviewTab = ({ error, loading, stats, onRefresh }: AdminOverviewTabProps) => {
  const { t } = useTranslation();

  return (
    <div className="admin-section">
      {error && <div className="admin-error-message">{error}</div>}

      {loading ? (
        <div className="admin-loading">{t('settings.loadingAdminStats')}</div>
      ) : (
        <div className="admin-stats-grid">
          <div className="admin-field admin-stat-card">
            <label>{t('settings.totalCards')}</label>
            <div className="admin-value">{formatNumber(stats?.total_cards ?? 0)}</div>
          </div>
          <div className="admin-field admin-stat-card">
            <label>{t('settings.totalUsers')}</label>
            <div className="admin-value">{formatNumber(stats?.total_users ?? 0)}</div>
          </div>
          <div className="admin-field admin-stat-card">
            <label>{t('settings.cardsWithStats')}</label>
            <div className="admin-value">{formatNumber(stats?.cards_with_stats ?? 0)}</div>
          </div>
          <div className="admin-field admin-stat-card">
            <label>{t('settings.statsToday')}</label>
            <div className="admin-value">{formatNumber(stats?.cards_stats_today ?? 0)}</div>
          </div>
        </div>
      )}

      <div className="admin-actions">
        <button onClick={onRefresh} className="button button-secondary" disabled={loading}>
          {t('settings.refreshAdminStats')}
        </button>
      </div>
    </div>
  );
};

export default AdminOverviewTab;
