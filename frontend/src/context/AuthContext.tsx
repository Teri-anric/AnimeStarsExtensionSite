import { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import axios from 'axios';
import { DefaultApi } from '../client';
import { createAuthenticatedClient } from '../utils/apiClient';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
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
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUsername = localStorage.getItem('username');
    
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
      setUsername(storedUsername);
    }
    
    setLoading(false);
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
      
      // Save token and user info
      localStorage.setItem('token', access_token);
      localStorage.setItem('username', username);
      
      setToken(access_token);
      setIsAuthenticated(true);
      setUsername(username);
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    // Clear token and user info
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    
    setToken(null);
    setIsAuthenticated(false);
    setUsername(null);
    
    // Optional: Call logout endpoint
    if (token) {
      try {
        // Create authenticated API client
        const apiClient = createAuthenticatedClient(DefaultApi);
        
        // Call logout endpoint using the client
        apiClient.readRootGet()
          .then(() => console.log('Logout successful'))
          .catch(error => console.error('Logout API call failed:', error));
      } catch (error) {
        console.error('Error during logout:', error);
      }
    }
  };

  const value = {
    isAuthenticated,
    token,
    username,
    login,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 