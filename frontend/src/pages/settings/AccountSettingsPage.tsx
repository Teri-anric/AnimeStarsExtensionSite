import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useDomain } from '../../context/DomainContext';
import ExtensionStatus from '../../components/ExtensionStatus';
import '../../styles/AccountSettings.css';

const AccountSettingsPage = () => {
  const { username } = useAuth();
  const { currentDomain, setCurrentDomain, availableDomains } = useDomain();
  const [successMessage, setSuccessMessage] = useState('');

  const handleDomainChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDomain = e.target.value;
    setCurrentDomain(newDomain);
    setSuccessMessage('Domain settings updated successfully');
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      setSuccessMessage('');
    }, 3000);
  };

  return (
    <div className="account-settings">
      <h1>Account Settings</h1>
      
      <div className="settings-container">
        <div className="settings-group">
          <h2>User Information</h2>
          <div className="user-info-item">
            <label>Username</label>
            <div className="user-value">{username}</div>
          </div>
        </div>
        
        <div className="settings-group">
          <h2>Browser Extension</h2>
          <div className="setting-description">
            Connect the Anime Stars browser extension to sync your card statistics and get enhanced features.
          </div>
          <ExtensionStatus />
        </div>
        
        <div className="settings-group">
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
            >
              {availableDomains.map((domain) => (
                <option key={domain} value={domain}>
                  {domain}
                </option>
              ))}
            </select>
          </div>
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

export default AccountSettingsPage; 