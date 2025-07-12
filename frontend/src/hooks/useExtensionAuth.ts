import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

interface ExtensionInfo {
  hasExtension: boolean;
  extensionVersion?: string;
  isConnected: boolean;
}

export interface UseExtensionAuthReturn {
  extensionInfo: ExtensionInfo;
  initializeExtensionToken: () => Promise<boolean>;
  isInitializing: boolean;
  error: string | null;
  clearError: () => void;
}

export const useExtensionAuth = (): UseExtensionAuthReturn => {
  const { isAuthenticated, token } = useAuth();
  const [extensionInfo, setExtensionInfo] = useState<ExtensionInfo>({
    hasExtension: false,
    isConnected: false
  });
  const [isInitializing, setIsInitializing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if extension is present via postMessage ping
  const pingExtension = useCallback(() => {
    window.postMessage({
      type: 'EXTENSION_PING',
      timestamp: Date.now()
    }, window.location.origin);
  }, []);

  // Request token from extension via postMessage
  const requestTokenFromExtension = useCallback((): Promise<boolean> => {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substr(2, 9);
      const timeout = setTimeout(() => {
        cleanup();
        reject(new Error('Extension token request timeout'));
      }, 30000);

      const handleResponse = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        if (event.data.type === 'EXTENSION_TOKEN_RESPONSE' && event.data.requestId === requestId) {
          cleanup();
          if (event.data.success) {
            resolve(true);
          } else {
            reject(new Error(event.data.error || 'Token request failed'));
          }
        }
      };

      const cleanup = () => {
        clearTimeout(timeout);
        window.removeEventListener('message', handleResponse);
      };

      window.addEventListener('message', handleResponse);
      
      window.postMessage({
        type: 'EXTENSION_REQUEST_TOKEN',
        requestId: requestId,
        timestamp: Date.now()
      }, window.location.origin);
    });
  }, []);

  // Initialize extension token from backend
  const initializeExtensionToken = useCallback(async (): Promise<boolean> => {
    if (!isAuthenticated || !token) {
      setError('User not authenticated');
      return false;
    }

    if (!extensionInfo.hasExtension) {
      setError('Extension not detected');
      return false;
    }

    setIsInitializing(true);
    setError(null);

    try {
      await requestTokenFromExtension();
      return true;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Extension token initialization failed:', errorMessage);
      return false;
    } finally {
      setIsInitializing(false);
    }
  }, [isAuthenticated, token, extensionInfo.hasExtension, requestTokenFromExtension]);

  // Check for extension presence on mount and periodically
  useEffect(() => {
    // Handle extension presence notifications
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      
      const { data } = event;
      if (data.type === 'EXTENSION_PRESENCE') {
        setExtensionInfo({
          hasExtension: data.hasExtension || false,
          extensionVersion: data.version || 'unknown',
          isConnected: data.isConnected || false
        });
      }
    };

    window.addEventListener('message', handleMessage);

    // Initial check
    pingExtension();

    // Check periodically for extension
    const interval = setInterval(pingExtension, 2000);

    return () => {
      clearInterval(interval);
      window.removeEventListener('message', handleMessage);
    };
  }, [pingExtension]);

  // Auto-initialize token when user authenticates and extension is available
  useEffect(() => {
    // Remove auto-initialization for now - only on explicit user action
    // We don't want to spam the extension with token requests
  }, []);

  return {
    extensionInfo,
    isInitializing,
    error,
    initializeExtensionToken,
    clearError: () => setError(null)
  };
}; 