import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

interface ExtensionInfo {
  hasExtension: boolean;
  extensionVersion?: string;
  isConnected: boolean;
}

interface UseExtensionAuthReturn {
  extensionInfo: ExtensionInfo;
  initializeExtensionToken: () => Promise<boolean>;
  isInitializing: boolean;
  error: string | null;
}

export const useExtensionAuth = (): UseExtensionAuthReturn => {
  const { isAuthenticated, token } = useAuth();
  const [extensionInfo, setExtensionInfo] = useState<ExtensionInfo>({
    hasExtension: false,
    isConnected: false
  });
  const [isInitializing, setIsInitializing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if extension is present and get its info
  const checkExtensionPresence = useCallback(() => {
    const extensionBridge = (window as any).extensionTokenBridge;
    
    if (extensionBridge && extensionBridge.hasExtension) {
      setExtensionInfo({
        hasExtension: true,
        extensionVersion: extensionBridge.version || 'unknown',
        isConnected: true
      });
      return true;
    } else {
      setExtensionInfo({
        hasExtension: false,
        isConnected: false
      });
      return false;
    }
  }, []);

  // Initialize extension token from backend
  const initializeExtensionToken = useCallback(async (): Promise<boolean> => {
    if (!isAuthenticated || !token) {
      setError('User not authenticated');
      return false;
    }

    setIsInitializing(true);
    setError(null);

    try {
      // Check if extension is present
      if (!checkExtensionPresence()) {
        throw new Error('Extension not detected');
      }

      // Generate new token from backend (same system as user tokens)
      const response = await fetch('/api/extension/token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to create extension token: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.access_token) {
        throw new Error('No access token available');
      }

      // Send token to extension via postMessage
      window.postMessage({
        type: 'ASS_EXTENSION_TOKEN_UPDATE',
        token: data.access_token,
        source: 'website_init'
      }, window.location.origin);

      // Also trigger custom event
      window.dispatchEvent(new CustomEvent('website_token_response', {
        detail: {
          type: 'token_response',
          success: true,
          token: data.access_token,
          source: 'website_init',
          timestamp: Date.now()
        }
      }));

      console.log('Extension token initialized successfully');
      return true;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Extension token initialization failed:', errorMessage);
      return false;
    } finally {
      setIsInitializing(false);
    }
  }, [isAuthenticated, token, checkExtensionPresence]);

  // Check for extension presence on mount and periodically
  useEffect(() => {
    // Initial check
    checkExtensionPresence();

    // Check periodically for extension
    const interval = setInterval(checkExtensionPresence, 2000);

    // Listen for extension ready events
    const handleExtensionReady = () => {
      checkExtensionPresence();
    };

    window.addEventListener('extension_ready', handleExtensionReady);

    return () => {
      clearInterval(interval);
      window.removeEventListener('extension_ready', handleExtensionReady);
    };
  }, [checkExtensionPresence]);

  // Auto-initialize token when user authenticates and extension is available
  useEffect(() => {
    if (isAuthenticated && extensionInfo.hasExtension && !isInitializing) {
      // Small delay to ensure everything is ready
      const timeout = setTimeout(() => {
        initializeExtensionToken();
      }, 1000);

      return () => clearTimeout(timeout);
    }
  }, [isAuthenticated, extensionInfo.hasExtension, isInitializing, initializeExtensionToken]);

  return {
    extensionInfo,
    initializeExtensionToken,
    isInitializing,
    error
  };
}; 