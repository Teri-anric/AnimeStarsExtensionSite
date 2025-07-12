import React from 'react';
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
    if (isInitializing) return 'Connecting...';
    if (extensionInfo.hasExtension && extensionInfo.isConnected) return 'Connected';
    if (extensionInfo.hasExtension && !extensionInfo.isConnected) return 'Detected (Not Connected)';
    return 'Not Detected';
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
        <span className="status-text">Extension: {getStatusText()}</span>
        {extensionInfo.extensionVersion && (
          <span className="status-version">v{extensionInfo.extensionVersion}</span>
        )}
      </div>

      {showDetails && (
        <div className="status-details">
          {!extensionInfo.hasExtension && (
            <div className="status-message info">
              <p>
                📥 Install the Anime Stars Browser Extension to sync your card statistics 
                and get enhanced features while browsing anime card sites.
              </p>
              <button 
                className="install-button"
                onClick={handleInstallExtension}
              >
                Install Extension
              </button>
            </div>
          )}

          {extensionInfo.hasExtension && !extensionInfo.isConnected && (
            <div className="status-message warning">
              <p>
                🔌 Extension detected but not connected. Click to establish connection.
              </p>
              <button 
                className="connect-button"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                {isInitializing ? 'Connecting...' : 'Connect Extension'}
              </button>
            </div>
          )}

          {extensionInfo.hasExtension && extensionInfo.isConnected && (
            <div className="status-message success">
              <div className="connection-info">
                <h4>🎉 Extension Connected Successfully!</h4>
                <p>
                  Your browser extension is connected and ready to sync card statistics.
                </p>
                
                <div className="features-active">
                  <h5>Active Features:</h5>
                  <ul>
                    <li>✅ Card statistics synchronization</li>
                    <li>✅ Real-time data updates</li>
                    <li>✅ Cross-platform card tracking</li>
                    <li>✅ Enhanced browsing experience</li>
                  </ul>
                </div>
              </div>
              
              <button 
                className="reconnect-button secondary"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                Refresh Connection
              </button>
            </div>
          )}

          {error && (
            <div className="status-message error">
              <p>❌ Connection Error: {error}</p>
              <button 
                className="retry-button"
                onClick={handleRetryConnection}
                disabled={isInitializing}
              >
                Retry
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExtensionStatus; 