import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDomain } from '../../context/DomainContext';
import { useAuth } from '../../context/AuthContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { AuthApi, UserResponse } from '../../client';
import { formatTimeAgo } from '../../utils/dateUtils';
import { useTranslation } from 'react-i18next';
import '../../styles/settings/AccountSettings.css';
import LanguageSwitcher from '../../components/LanguageSwitcher';

const AccountSettings = () => {
  const { t } = useTranslation();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { currentDomain, setCurrentDomain, availableDomains } = useDomain();
  const [successMessage, setSuccessMessage] = useState('');
  const [userInfo, setUserInfo] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) {
      return;
    }
    if (!isAuthenticated) {
      setLoading(false);
      setUserInfo(null);
      setError(null);
      return;
    }

    const fetchUserInfo = async () => {
      try {
        setLoading(true);
        setError(null);
        const apiClient = createAuthenticatedClient(AuthApi);
        const response = await apiClient.readUsersMeApiAuthMeGet();
        setUserInfo(response.data);
      } catch (err) {
        console.error('Failed to fetch user info:', err);
        setError(t('settings.failedToLoadUserInfo'));
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, [authLoading, isAuthenticated, t]);

  const handleDomainChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDomain = e.target.value;
    setCurrentDomain(newDomain);
    setSuccessMessage(t('settings.domainSettingsUpdated'));
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      setSuccessMessage('');
    }, 3000);
  };



  const userSection = (() => {
    if (authLoading || (isAuthenticated && loading)) {
      return (
        <div className="setting-item">
          <div className="loading">{t('settings.loadingUserInfo')}</div>
        </div>
      );
    }
    if (!isAuthenticated) {
      return (
        <div className="setting-item">
          <p className="setting-description">{t('auth.pleaseLogIn')}</p>
          <Link to="/login" className="button button-secondary">
            {t('auth.login')}
          </Link>
        </div>
      );
    }
    if (error) {
      return (
        <div className="setting-item">
          <div className="error-message">{error}</div>
        </div>
      );
    }
    if (userInfo) {
      return (
        <>
          <div className="setting-item">
            <label>{t('common.username')}</label>
            <div className="setting-value">{userInfo.username}</div>
          </div>
          <div className="setting-item">
            <label>{t('settings.accountCreated')}</label>
            <div className="setting-value">{formatTimeAgo(userInfo.created_at, t)}</div>
          </div>
          <LanguageSwitcher />
        </>
      );
    }
    return null;
  })();

  return (
    <div className="account-settings-content">
      <div className="settings-section">
        <h2>{t('settings.userInformation')}</h2>
        {userSection}
      </div>
      
      <div className="settings-section">
        <h2>{t('settings.siteSettings')}</h2>
        
        <div className="setting-item">
          <label htmlFor="domain-setting">{t('settings.cardDomain')}</label>
          <div className="setting-description">
            {t('settings.cardDomainDescription')}
          </div>
          <select 
            id="domain-setting" 
            value={currentDomain}
            onChange={handleDomainChange}
            className="setting-input"
          >
            {availableDomains.map((domain) => (
              <option key={domain} value={domain}>
                {domain}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
    </div>
  );
};

export default AccountSettings;