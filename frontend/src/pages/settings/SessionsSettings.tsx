import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { formatTimeAgo, formatDateTime } from '../../utils/dateUtils';
import '../../styles/settings/SessionsSettings.css';

interface Session {
  id: string;
  created_at: string;
  expire_at: string;
  is_current: boolean;
}

const SessionsSettings = () => {
  const { t } = useTranslation();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiAvailable, setApiAvailable] = useState(false);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/sessions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data);
        setApiAvailable(true);
      } else {
        setApiAvailable(false);
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setApiAvailable(false);
      setError(t('settings.apiNotAvailable'));
    } finally {
      setLoading(false);
    }
  };

  const revokeSession = async (sessionId: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await fetchSessions();
      } else {
        throw new Error('Failed to revoke session');
      }
    } catch (err) {
      console.error('Failed to revoke session:', err);
      setError(t('settings.failedToRevokeSession'));
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);


  if (!apiAvailable && !loading) {
    return (
      <div className="sessions-content">
        <div className="settings-section">
          <h2>{t('settings.sessionManagement')}</h2>
          <div className="setting-description">
            {t('settings.sessionManagementDescription')}
          </div>
        </div>

        <div className="feature-coming-soon">
          <div className="feature-icon">🚧</div>
          <h3>{t('settings.featureComingSoon')}</h3>
          <p className="feature-description">
            {t('settings.featureDescription')}
          </p>

          <div className="feature-benefits">
            <h4>{t('settings.whatYouWillBeAbleToDo')}</h4>
            <ul>
              <li>{t('settings.viewAllSessions')}</li>
              <li>{t('settings.seeSessionInfo')}</li>
              <li>{t('settings.identifyDevices')}</li>
              <li>{t('settings.revokeSessions')}</li>
              <li>{t('settings.monitorSecurity')}</li>
            </ul>
          </div>

          <div className="feature-status">
            <div className="status-item">
              <span className="status-label">{t('settings.backendApi')}</span>
              <span className="status-value ready">{t('settings.ready')}</span>
            </div>
            <div className="status-item">
              <span className="status-label">{t('settings.frontendUi')}</span>
              <span className="status-value ready">{t('settings.ready')}</span>
            </div>
            <div className="status-item">
              <span className="status-label">{t('settings.deployment')}</span>
              <span className="status-value pending">{t('settings.pending')}</span>
            </div>
          </div>
        </div>

        <div className="settings-actions">
          <button
            onClick={fetchSessions}
            className="button button-secondary"
          >
            {t('settings.checkApiStatus')}
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="sessions-content">
        <div className="loading">
          {t('settings.loadingSessions')}
        </div>
      </div>
    );
  }

  return (
    <div className="sessions-content">
      <div className="settings-section">
        <h2>{t('settings.sessionManagement')}</h2>
        <div className="setting-description">
          {t('settings.sessionManagementDescription')}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchSessions} className="button button-secondary">
            {t('settings.retry')}
          </button>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="no-sessions">
          <p>{t('settings.noActiveSessions')}</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map((session) => (
            <div key={session.id} className={`session-item ${session.is_current ? 'current-session' : ''}`}>
              <div className="session-info">
                <div className="session-header">
                  <span className="session-id">{t('settings.sessionId')} {session.id.slice(0, 8)}...</span>
                  {session.is_current && (
                    <span className="current-badge">{t('settings.currentSession')}</span>
                  )}
                </div>
                <div className="session-details">
                  <p><strong>{t('settings.created')}</strong> {formatTimeAgo(session.created_at, t)}</p>
                  <p><strong>{t('settings.expires')}</strong> {formatDateTime(session.expire_at)}</p>
                </div>
              </div>
              {!session.is_current && (
                <button
                  onClick={() => revokeSession(session.id)}
                  className="button button-danger"
                >
                  {t('settings.revoke')}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="settings-actions">
        <button onClick={fetchSessions} className="button button-secondary">
          {t('settings.refreshSessions')}
        </button>
      </div>
    </div>
  );
};

export default SessionsSettings;