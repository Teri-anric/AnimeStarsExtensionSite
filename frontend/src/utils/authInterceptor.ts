import axios from 'axios';

// Global variable to store logout function
let logoutFunction: (() => void) | null = null;

// Set logout function from AuthContext
export const setLogoutFunction = (logout: () => void) => {
  logoutFunction = logout;
};

// Create axios interceptor for handling 401 errors
export const setupAuthInterceptor = () => {
  // Request interceptor to add token to all requests
  axios.interceptors.request.use(
    (config: any) => {
      const token = localStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: any) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor to handle 401 errors
  axios.interceptors.response.use(
    (response: any) => {
      return response;
    },
    (error: any) => {
      if (error.response?.status === 401) {
        console.log('Token expired or invalid, logging out...');
        
        // Clear local storage
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        
        // Call logout function if available
        if (logoutFunction) {
          logoutFunction();
        }
        
        // Redirect to login page
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};

// Function to check if token is valid
export const checkTokenValidity = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      return false;
    }

    // Make a simple API call to check if token is valid using fetch
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/health`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    return response.status === 200;
  } catch (error) {
    console.log('Token validation failed:', error);
    return false;
  }
};