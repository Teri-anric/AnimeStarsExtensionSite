import { Configuration, DefaultApi, HealthApi, CardApi, DeckApi, CardStatsApi } from '../client';
import { setupAuthInterceptor } from './authInterceptor';

const basePath = import.meta.env.VITE_API_URL;

// Setup auth interceptor
setupAuthInterceptor();

/**
 * Creates an authenticated API client with the stored token
 */
export const createAuthenticatedClient = <T extends DefaultApi | HealthApi | CardApi | DeckApi | CardStatsApi>(
  ApiClass: new (config: Configuration) => T
): T => {
  const token = localStorage.getItem('token');
  
  const config = new Configuration({
    basePath,
    accessToken: token || undefined
  });
  
  return new ApiClass(config);
};

/**
 * Creates a basic API client without authentication
 */
export const createClient = <T extends DefaultApi | HealthApi | CardApi | DeckApi | CardStatsApi>(
  ApiClass: new (config: Configuration) => T
): T => {
  const config = new Configuration({
    basePath
  });
  
  return new ApiClass(config);
}; 