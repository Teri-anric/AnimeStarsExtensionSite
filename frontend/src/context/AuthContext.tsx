import { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import axios from 'axios';
import { AuthApi } from '../client';
import { createAuthenticatedClient } from '../utils/apiClient';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
  isAdmin: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchCurrentUser = async (accessToken: string): Promise<{ username: string; is_admin: boolean }> => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch current user');
    }

    return response.json();
  };

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('token');

    const initializeAuth = async () => {
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await fetchCurrentUser(storedToken);
        localStorage.setItem('username', currentUser.username);
        localStorage.setItem('is_admin', String(currentUser.is_admin));

        setToken(storedToken);
        setIsAuthenticated(true);
        setUsername(currentUser.username);
        setIsAdmin(currentUser.is_admin);
      } catch (error) {
        console.error('Failed to restore auth state:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('is_admin');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post(import.meta.env.VITE_API_URL + '/api/auth/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      const { access_token } = response.data;
      const currentUser = await fetchCurrentUser(access_token);
      
      // Save token and user info
      localStorage.setItem('token', access_token);
      localStorage.setItem('username', currentUser.username);
      localStorage.setItem('is_admin', String(currentUser.is_admin));
      
      setToken(access_token);
      setIsAuthenticated(true);
      setUsername(currentUser.username);
      setIsAdmin(currentUser.is_admin);
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('is_admin');
      return false;
    }
  };

  const logout = async () => {
    // Call logout endpoint first
    if (token) {
      try {
        const apiClient = createAuthenticatedClient(AuthApi);
        await apiClient.logoutApiAuthLogoutPost();
        console.log('Logout API call successful');
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      }
    }
    
    // Clear token and user info
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('is_admin');
    
    setToken(null);
    setIsAuthenticated(false);
    setUsername(null);
    setIsAdmin(false);
  };

  const value = {
    isAuthenticated,
    token,
    username,
    isAdmin,
    login,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 