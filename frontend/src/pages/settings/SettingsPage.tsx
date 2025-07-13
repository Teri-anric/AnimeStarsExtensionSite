import { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import AccountSettings from './AccountSettings';
import ExtensionSettings from './ExtensionSettings';
import SessionsSettings from './SessionsSettings';
import { useTranslation } from 'react-i18next';
import '../../styles/settings/index.css';


const SettingsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState(() => {
    const path = location.pathname;
    const tab = SETTINGS_TABS.find(tab => path === tab.path);
    return tab?.id || 'account';
  });
  
  const SETTINGS_TABS = [
    {
      id: 'account',
      label: t('navigation.account'),
      path: '/settings',
    },
    {
      id: 'extension',
      label: t('navigation.extension'),
      path: '/settings/extension',
    },
    {
      id: 'sessions',
      label: t('navigation.sessions'),
      path: '/settings/sessions',
    }
  ];

  useEffect(() => {
    const path = location.pathname;
    const tab = SETTINGS_TABS.find(tab => path === tab.path);
    setActiveTab(tab?.id || 'account');
  }, [location.pathname]);

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>{t('settings.title')}</h1>
      </div>
      
      <div className="settings-layout">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {SETTINGS_TABS.map((tab) => (
              <a
                key={tab.id}
                href={tab.path}
                className={`settings-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  setActiveTab(tab.id);
                  navigate(tab.path);
                }}
              >
                <span className="nav-label">{tab.label}</span>
              </a>
            ))}
          </nav>
        </div>
        
        <div className="settings-content">
          <Routes>
            <Route path="/" element={<AccountSettings />} />
            <Route path="/extension" element={<ExtensionSettings />} />
            <Route path="/sessions" element={<SessionsSettings />} />
            <Route path="*" element={<Navigate to="/settings" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;