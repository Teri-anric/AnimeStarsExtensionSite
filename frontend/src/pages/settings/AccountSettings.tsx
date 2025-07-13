import { useState, useEffect } from 'react';
import { useDomain } from '../../context/DomainContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { AuthApi, UserResponse } from '../../client';
import '../../styles/settings/AccountSettings.css';

const AccountSettings = () => {
  const { currentDomain, setCurrentDomain, availableDomains } = useDomain();
  const [successMessage, setSuccessMessage] = useState('');
  const [userInfo, setUserInfo] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        setLoading(true);
        setError(null);
        const apiClient = createAuthenticatedClient(AuthApi);
        const response = await apiClient.readUsersMeApiAuthMeGet();
        setUserInfo(response.data);
      } catch (err) {
        console.error('Failed to fetch user info:', err);
        setError('Failed to load user information');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  const handleDomainChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDomain = e.target.value;
    setCurrentDomain(newDomain);
    setSuccessMessage('Domain settings updated successfully');
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      setSuccessMessage('');
    }, 3000);
  };

  const formatTimeAgo = (dateString: string) => {
    try {
      const now = new Date();
      const date = new Date(dateString);
      const diffInMs = now.getTime() - date.getTime();
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      const diffInDays = Math.floor(diffInHours / 24);
      const diffInWeeks = Math.floor(diffInDays / 7);
      const diffInMonths = Math.floor(diffInDays / 30);
      const diffInYears = Math.floor(diffInDays / 365);

      if (diffInMs < 0) return 'Future date';
      if (diffInHours < 1) {
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
        return diffInMinutes <= 0 ? 'Just now' : `${diffInMinutes}m ago`;
      } else if (diffInHours < 24) {
        return `${diffInHours}h ago`;
      } else if (diffInDays < 7) {
        return `${diffInDays}d ago`;
      } else if (diffInWeeks < 4) {
        return `${diffInWeeks}w ago`;
      } else if (diffInMonths < 12) {
        return `${diffInMonths}mo ago`;
      } else {
        return `${diffInYears}y ago`;
      }
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="account-settings-content">
        <div className="settings-section">
          <h2>User Information</h2>
          <div className="setting-item">
            <div className="loading">Loading user information...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="account-settings-content">
        <div className="settings-section">
          <h2>User Information</h2>
          <div className="setting-item">
            <div className="error-message">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="account-settings-content">
      <div className="settings-section">
        <h2>User Information</h2>
        {userInfo && (
          <>
            <div className="setting-item">
              <label>Username</label>
              <div className="setting-value">{userInfo.username}</div>
            </div>
            <div className="setting-item">
              <label>Account Created</label>
              <div className="setting-value">{formatTimeAgo(userInfo.created_at)}</div>
            </div>
          </>
        )}
      </div>
      
      <div className="settings-section">
        <h2>Site Settings</h2>
        
        <div className="setting-item">
          <label htmlFor="domain-setting">Card Domain</label>
          <div className="setting-description">
            Select the domain used to display card images and media
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