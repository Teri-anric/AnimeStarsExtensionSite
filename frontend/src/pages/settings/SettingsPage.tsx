import { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import AccountSettings from './AccountSettings';
import ExtensionSettings from './ExtensionSettings';
import SessionsSettings from './SessionsSettings';
import '../../styles/SettingsPage.css';

const SettingsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(() => {
    const path = location.pathname;
    if (path.includes('/sessions')) return 'sessions';
    return 'account';
  });

  useEffect(() => {
    const path = location.pathname;
    if (path.includes('/sessions')) {
      setActiveTab('sessions');
    } else {
      setActiveTab('account');
    }
  }, [location.pathname]);

  const tabs = [
    {
      id: 'account',
      label: 'Account',
      path: '/settings',
    },
    {
      id: 'extension',
      label: 'Browser Extension',
      path: '/settings/extension',
    },
    {
      id: 'sessions',
      label: 'Sessions',
      path: '/settings/sessions',
    }
  ];

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Settings</h1>
      </div>
      
      <div className="settings-layout">
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map((tab) => (
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