import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
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

  useEffect(() => {
    // Listen for extension token requests
    const handleExtensionRequest = (event: CustomEvent) => {
      console.log('Extension token request received:', event.detail);
      
      if (event.detail && event.detail.type === 'token_request') {
        setRequestData(event.detail);
        setIsVisible(true);
      }
    };

    // Listen for postMessage requests as fallback
    const handlePostMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      
      if (event.data && event.data.type === 'ASS_EXTENSION_TOKEN_REQUEST') {
        console.log('Extension token request via postMessage:', event.data);
        setRequestData(event.data);
        setIsVisible(true);
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
        type: 'ASS_EXTENSION_TOKEN_RESPONSE',
        ...responseData
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
      type: 'ASS_EXTENSION_TOKEN_RESPONSE',
      ...responseData
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
            <h3>Extension Access Request</h3>
            <button className="close-button" onClick={handleClose}>×</button>
          </div>
          <div className="modal-content">
            <div className="extension-icon">🔌</div>
            <p>The Anime Stars Extension is requesting access, but you need to log in first.</p>
            <div className="modal-actions">
              <button className="deny-button" onClick={() => handleDeny('User not logged in')}>
                Close
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
          <h3>Connect Browser Extension</h3>
          <button className="close-button" onClick={handleClose}>×</button>
        </div>
        
        <div className="modal-content">
          <div className="extension-icon">🔌</div>
          
          <div className="request-info">
            <h4>Extension Access Request</h4>
            <p>
              The <strong>Anime Stars Extension</strong> is requesting access to your account 
              to provide enhanced features like card statistics and data synchronization.
            </p>
            
            {requestData && (
              <div className="request-details">
                <small>Request from: {requestData.extensionId}</small>
              </div>
            )}
          </div>

          <div className="features-list">
            <h5>This will allow the extension to:</h5>
            <ul>
              <li>✅ Fetch card statistics from the API</li>
              <li>✅ Synchronize card data</li>
              <li>✅ Access your saved preferences</li>
              <li>❌ Modify your account data</li>
              <li>❌ Access sensitive information</li>
            </ul>
          </div>

          <div className="user-info">
            <p>Sharing access for: <strong>{username}</strong></p>
          </div>

          <div className="modal-actions">
            <button 
              className="deny-button" 
              onClick={() => handleDeny('User denied access')}
              disabled={isProcessing}
            >
              Deny Access
            </button>
            <button 
              className="approve-button" 
              onClick={handleApprove}
              disabled={isProcessing}
            >
              {isProcessing ? 'Connecting...' : 'Allow Access'}
            </button>
          </div>

          <div className="security-note">
            <small>
              🔒 Your token will only be shared with the verified Anime Stars Extension. 
              You can revoke access anytime by logging out.
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtensionTokenModal; 