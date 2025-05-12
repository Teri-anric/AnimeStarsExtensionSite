import { Configuration, DefaultApi, HealthApi } from '../client';

/**
 * Creates an authenticated API client with the stored token
 */
export const createAuthenticatedClient = <T extends DefaultApi | HealthApi>(
  ApiClass: new (config: Configuration) => T
): T => {
  const token = localStorage.getItem('token');
  
  const config = new Configuration({
    basePath: 'http://localhost:8000',
    accessToken: token || undefined,
    isJsonMime: () => true
  });
  
  return new ApiClass(config);
};

/**
 * Creates a basic API client without authentication
 */
export const createClient = <T extends DefaultApi | HealthApi>(
  ApiClass: new (config: Configuration) => T
): T => {
  const config = new Configuration({
    basePath: 'http://localhost:8000',
    isJsonMime: () => true
  });
  
  return new ApiClass(config);
}; 