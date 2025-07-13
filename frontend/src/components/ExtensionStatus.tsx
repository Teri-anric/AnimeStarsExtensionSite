import React from 'react';
import { useTranslation } from 'react-i18next';
import { useExtensionAuth } from '../hooks/useExtensionAuth';
import '../styles/components/ExtensionStatus.css';

interface ExtensionStatusProps {
  showDetails?: boolean;
  className?: string;
}

const ExtensionStatus: React.FC<ExtensionStatusProps> = ({ 
  showDetails = true, 
  className = '' 
}) => {
  const { t } = useTranslation();
  const { 
    extensionInfo, 
    initializeExtensionToken, 
    isInitializing, 
    error 
  } = useExtensionAuth();

  const getStatusIcon = () => {
    if (isInitializing) return '⏳';
    if (extensionInfo.hasExtension && extensionInfo.isConnected) return '✅';
    if (extensionInfo.hasExtension && !extensionInfo.isConnected) return '⚠️';
    return '❌';
  };

  const getStatusText = () => {
    if (isInitializing) return t('extensionStatus.connecting');
    if (extensionInfo.hasExtension && extensionInfo.isConnected) return t('extensionStatus.connected');
    if (extensionInfo.hasExtension && !extensionInfo.isConnected) return t('extensionStatus.detectedNotConnected');
    return t('extensionStatus.notDetected');
  };

  const getStatusClass = () => {
    if (isInitializing) return 'status-connecting';
    if (extensionInfo.hasExtension && extensionInfo.isConnected) return 'status-connected';
    if (extensionInfo.hasExtension && !extensionInfo.isConnected) return 'status-warning';
    return 'status-disconnected';
  };

  const handleRetryConnection = async () => {
    try {
      await initializeExtensionToken();
    } catch (err) {
      console.error('Failed to retry connection:', err);
    }
  };

  const handleInstallExtension = () => {
    // This could open installation instructions or Chrome Web Store
    window.open('https://github.com/your-repo/anime-stars-extension', '_blank');
  };

  return (
    <div className={`extension-status ${className}`}>
      <div className={`status-indicator ${getStatusClass()}`}>
        <span className="status-icon">{getStatusIcon()}</span>
        <span className="status-text">{t('extensionStatus.extension')} {getStatusText()}</span>
        {extensionInfo.extensionVersion && (
          <span className="status-version">v{extensionInfo.extensionVersion}</span>
        )}
      </div>

      {showDetails && (
        <div className="status-details">
          {!extensionInfo.hasExtension && (
            <div className="status-message info">
              <p>
                {t('extensionStatus.installMessage')}
              </p>
              <button 
                className="install-button"
                onClick={handleInstallExtension}
              >
                {t('extensionStatus.installExtension')}
              </button>
            </div>
          )}

          {extensionInfo.hasExtension && !extensionInfo.isConnected && (
            <div className="status-message warning">
              <p>
                {t('extensionStatus.detectedNotConnectedMessage')}
              </p>
              <button 
                className="connect-button"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                {isInitializing ? t('extensionStatus.connecting') : t('extensionStatus.connectExtension')}
              </button>
            </div>
          )}

          {extensionInfo.hasExtension && extensionInfo.isConnected && (
            <div className="status-message success">
              <div className="connection-info">
                <h4>{t('extensionStatus.connectedSuccessfully')}</h4>
                <p>
                  {t('extensionStatus.connectedMessage')}
                </p>
                
                <div className="features-active">
                  <h5>{t('extensionStatus.activeFeatures')}</h5>
                  <ul>
                    <li>{t('extensionStatus.cardStatsSync')}</li>
                    <li>{t('extensionStatus.realTimeUpdates')}</li>
                    <li>{t('extensionStatus.crossPlatformTracking')}</li>
                    <li>{t('extensionStatus.enhancedBrowsing')}</li>
                  </ul>
                </div>
              </div>
              
              <button 
                className="reconnect-button secondary"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                {t('extensionStatus.refreshConnection')}
              </button>
            </div>
          )}

          {error && (
            <div className="status-message error">
              <p>{t('extensionStatus.connectionError')} {error}</p>
              <button 
                className="retry-button"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                {t('extensionStatus.retryConnection')}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExtensionStatus; 