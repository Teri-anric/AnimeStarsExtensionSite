import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import '../styles/components/ExtensionTokenModal.css';

interface TokenRequestData {
  type: string;
  extensionId: string;
  timestamp: number;
  origin: string;
}

interface ExtensionTokenModalProps {
  // Optional props for testing
  isVisible?: boolean;
  onClose?: () => void;
}

const ExtensionTokenModal: React.FC<ExtensionTokenModalProps> = ({ 
  isVisible: forcedVisible, 
  onClose: forcedOnClose 
}) => {
  const { token, username, isAuthenticated } = useAuth();
  const [isVisible, setIsVisible] = useState(forcedVisible || false);
  const [requestData, setRequestData] = useState<TokenRequestData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    // Listen for extension token requests
    const handleExtensionRequest = (event: CustomEvent) => {
      console.log('Extension token request received:', event.detail);
      
      try {
        // Safe access to event.detail properties
        const detail = event.detail;
        if (detail && (detail.type === 'token_request' || detail.type === 'ASS_EXTENSION_TOKEN_REQUEST')) {
          setRequestData({
            type: detail.type || 'token_request',
            extensionId: detail.extensionId || 'unknown',
            timestamp: detail.timestamp || Date.now(),
            origin: detail.origin || 'extension'
          });
          setIsVisible(true);
        }
      } catch (error) {
        console.warn('Error accessing event.detail properties:', error);
        // Fallback: show modal anyway if we got an extension request
        setRequestData({
          type: 'token_request',
          extensionId: 'unknown',
          timestamp: Date.now(),
          origin: 'extension'
        });
        setIsVisible(true);
      }
    };

    // Listen for postMessage requests as fallback
    const handlePostMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      
      try {
        if (event.data && event.data.type === 'ASS_EXTENSION_TOKEN_REQUEST') {
          console.log('Extension token request via postMessage:', event.data);
          setRequestData(event.data);
          setIsVisible(true);
        }
      } catch (error) {
        console.warn('Error accessing postMessage data:', error);
      }
    };

    // Add event listeners
    window.addEventListener('extension_token_request', handleExtensionRequest as EventListener);
    window.addEventListener('message', handlePostMessage);

    return () => {
      window.removeEventListener('extension_token_request', handleExtensionRequest as EventListener);
      window.removeEventListener('message', handlePostMessage);
    };
  }, []);

  const handleApprove = async () => {
    if (!token || !isAuthenticated) {
      handleDeny('User is not authenticated');
      return;
    }

    setIsProcessing(true);

    try {
      // Send token to extension
      const responseData = {
        type: 'token_response',
        success: true,
        token: token,
        username: username,
        timestamp: Date.now()
      };

      // Send via custom event
      window.dispatchEvent(new CustomEvent('website_token_response', {
        detail: responseData
      }));

      // Also send via postMessage for compatibility
      window.postMessage({
        ...responseData,
        type: 'ASS_EXTENSION_TOKEN_RESPONSE'
      }, window.location.origin);

      console.log('Token shared with extension successfully');
      
      // Close modal after short delay
      setTimeout(() => {
        handleClose();
      }, 1000);

    } catch (error) {
      console.error('Error sharing token with extension:', error);
      handleDeny('Failed to share token');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeny = (reason?: string) => {
    console.log('Token request denied:', reason);
    
    const responseData = {
      type: 'token_response',
      success: false,
      error: reason || 'User denied access',
      timestamp: Date.now()
    };

    // Send denial response
    window.dispatchEvent(new CustomEvent('website_token_response', {
      detail: responseData
    }));

    window.postMessage({
      ...responseData,
      type: 'ASS_EXTENSION_TOKEN_RESPONSE'
    }, window.location.origin);

    handleClose();
  };

  const handleClose = () => {
    setIsVisible(false);
    setRequestData(null);
    setIsProcessing(false);
    forcedOnClose?.();
  };

  if (!isVisible && !forcedVisible) {
    return null;
  }

  if (!isAuthenticated) {
    return (
      <div className="extension-token-modal-overlay">
        <div className="extension-token-modal">
          <div className="modal-header">
            <h3>{t('extension.accessRequest')}</h3>
            <button className="close-button" onClick={handleClose}>×</button>
          </div>
          <div className="modal-content">
            <div className="extension-icon">🔌</div>
            <p>{t('extension.needLoginFirst')}</p>
            <div className="modal-actions">
              <button className="deny-button" onClick={() => handleDeny(t('extension.userNotLoggedIn'))}>
                {t('common.close')}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="extension-token-modal-overlay">
      <div className="extension-token-modal">
        <div className="modal-header">
          <h3>{t('extension.title')}</h3>
          <button className="close-button" onClick={handleClose}>×</button>
        </div>
        
        <div className="modal-content">
          <div className="extension-icon">🔌</div>
          
          <div className="request-info">
            <h4>{t('extension.accessRequest')}</h4>
            <p>
              {t('extension.requestDescription')}
            </p>
            
            {requestData && (
              <div className="request-details">
                <small>{t('extension.requestFrom', { extensionId: requestData.extensionId })}</small>
              </div>
            )}
          </div>

          <div className="features-list">
            <h5>{t('extension.featuresTitle')}</h5>
            <ul>
              <li>✅ {t('extension.featureFetchStats')}</li>
              <li>✅ {t('extension.featureSyncData')}</li>
              <li>✅ {t('extension.featureAccessPreferences')}</li>
              <li>❌ {t('extension.featureNoModifyData')}</li>
              <li>❌ {t('extension.featureNoSensitiveInfo')}</li>
            </ul>
          </div>

          <div className="user-info">
            <p>{t('extension.sharingFor', { username })}</p>
          </div>

          <div className="modal-actions">
            <button 
              className="deny-button" 
              onClick={() => handleDeny(t('extension.userDeniedAccess'))}
              disabled={isProcessing}
            >
              {t('extension.denyAccess')}
            </button>
            <button 
              className="approve-button" 
              onClick={handleApprove}
              disabled={isProcessing}
            >
              {isProcessing ? t('extension.connecting') : t('extension.allowAccess')}
            </button>
          </div>

          <div className="security-note">
            <small>
              🔒 {t('extension.securityNote')}
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtensionTokenModal; 