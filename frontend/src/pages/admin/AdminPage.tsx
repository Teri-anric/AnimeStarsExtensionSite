import { useEffect, useMemo } from 'react';
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import '../../styles/admin/AdminPage.css';
import AdminOverviewTab from './components/AdminOverviewTab';
import AdminBannerTab from './components/AdminBannerTab';
import AdminMenu from './components/AdminMenu';
import { useAdminStats } from './hooks/useAdminStats';
import { useAdminBanner } from './hooks/useAdminBanner';

const AdminPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isAuthenticated, loading: authLoading, isAdmin } = useAuth();
  const { stats, loading, error, fetchStats } = useAdminStats(t);
  const {
    bannerLoading,
    bannerSaving,
    bannerError,
    bannerSuccess,
    bannerForm,
    setBannerForm,
    fetchBannerConfig,
    saveBannerConfig,
  } = useAdminBanner(t);
  const adminTabs = useMemo(
    () => [
      {
        id: 'overview',
        label: 'settings.adminOverview',
        path: '/admin',
      },
      {
        id: 'banner',
        label: 'settings.adminExtensionBanner',
        path: '/admin/banner',
      },
    ],
    [],
  );
  const activeTab = location.pathname.startsWith('/admin/banner') ? 'banner' : 'overview';

  useEffect(() => {
    if (authLoading || !isAuthenticated || !isAdmin) {
      return;
    }
    if (location.pathname.startsWith('/admin/banner')) {
      fetchBannerConfig();
      return;
    }
    fetchStats();
  }, [authLoading, fetchBannerConfig, fetchStats, isAdmin, isAuthenticated, location.pathname]);

  const iframeUrl = useMemo(
    () => `${import.meta.env.VITE_API_URL}/api/extension/banner-iframe`,
    [],
  );
  const iframeCode = useMemo(
    () =>
      `<iframe src="${iframeUrl}" style="width:100%;min-height:90px;border:0;" loading="lazy" referrerpolicy="no-referrer"></iframe>`,
    [iframeUrl],
  );

  if (authLoading) {
    return <div className="admin-loading">{t('settings.loadingAdminStats')}</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="admin-guard">
        <h2>{t('settings.adminPanel')}</h2>
        <p>{t('auth.pleaseLogIn')}</p>
        <Link to="/login" className="button button-secondary">
          {t('auth.login')}
        </Link>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="admin-guard">
        <h2>{t('settings.adminPanel')}</h2>
        <p>{t('settings.adminAccessDenied')}</p>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="admin-layout">
        <aside className="admin-sidebar">
          <AdminMenu
            tabs={adminTabs.map((tab) => ({ ...tab, label: t(tab.label) }))}
            activeTab={activeTab}
            onNavigate={(path) => navigate(path)}
          />
        </aside>

        <section className="admin-content">
          <div className="admin-header">
            <h1>{t('settings.adminPanel')}</h1>
            <p>{t('settings.adminPanelDescription')}</p>
          </div>
          <Routes>
            <Route
              index
              element={(
                <AdminOverviewTab error={error} loading={loading} stats={stats} onRefresh={fetchStats} />
              )}
            />
            <Route
              path="banner"
              element={(
                <AdminBannerTab
                  bannerLoading={bannerLoading}
                  bannerSaving={bannerSaving}
                  bannerError={bannerError}
                  bannerSuccess={bannerSuccess}
                  bannerForm={bannerForm}
                  setBannerForm={setBannerForm}
                  iframeUrl={iframeUrl}
                  iframeCode={iframeCode}
                  onSave={saveBannerConfig}
                  onRefresh={fetchBannerConfig}
                />
              )}
            />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Routes>
        </section>
      </div>
    </div>
  );
};

export default AdminPage;
