import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../../styles/SessionsPage.css';

interface Session {
  id: string;
  created_at: string;
  expire_at: string;
  is_current: boolean;
}

const SessionsPage = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiAvailable, setApiAvailable] = useState(false);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to fetch sessions from API
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
        // API not available yet, show coming soon
        setApiAvailable(false);
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setApiAvailable(false);
      setError('API not available yet');
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
        // Refresh sessions list
        await fetchSessions();
      } else {
        throw new Error('Failed to revoke session');
      }
    } catch (err) {
      console.error('Failed to revoke session:', err);
      setError('Failed to revoke session');
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // Show coming soon page if API is not available
  if (!apiAvailable && !loading) {
    return (
      <div className="sessions-page">
        <div className="sessions-header">
          <h1>Active Sessions</h1>
          <Link to="/settings" className="back-link">
            ← Back to Settings
          </Link>
        </div>
        
        <div className="sessions-container">
          <div className="sessions-info-group">
            <h2>Session Management</h2>
            <div className="info-description">
              Manage your active sessions across different devices and browsers. 
              You can view all your current sessions and revoke access from devices you no longer use.
            </div>
          </div>
          
          <div className="feature-coming-soon-group">
            <div className="feature-icon">🚧</div>
            <h2>Feature Coming Soon</h2>
            <p className="feature-description">
              The session management feature is currently being developed and will be available soon.
            </p>
            
            <div className="feature-benefits">
              <h3>What you'll be able to do:</h3>
              <ul>
                <li>View all your active sessions across devices</li>
                <li>See when each session was created and expires</li>
                <li>Identify which device and browser each session belongs to</li>
                <li>Revoke sessions from devices you no longer use</li>
                <li>Monitor your account security</li>
              </ul>
            </div>
            
            <div className="feature-status">
              <div className="status-item">
                <span className="status-label">Backend API:</span>
                <span className="status-value ready">Ready</span>
              </div>
              <div className="status-item">
                <span className="status-label">Frontend UI:</span>
                <span className="status-value ready">Ready</span>
              </div>
              <div className="status-item">
                <span className="status-label">Deployment:</span>
                <span className="status-value pending">Pending</span>
              </div>
            </div>
          </div>
          
          <div className="sessions-actions">
            <button 
              onClick={fetchSessions} 
              className="refresh-button"
            >
              Check API Status
            </button>
            <Link to="/settings" className="settings-link-button">
              Back to Settings
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="sessions-page">
        <div className="sessions-header">
          <h1>Active Sessions</h1>
          <Link to="/settings" className="back-link">
            ← Back to Settings
          </Link>
        </div>
        
        <div className="sessions-container">
          <div className="loading">
            Loading sessions...
          </div>
        </div>
      </div>
    );
  }

  // Show actual sessions page
  return (
    <div className="sessions-page">
      <div className="sessions-header">
        <h1>Active Sessions</h1>
        <Link to="/settings" className="back-link">
          ← Back to Settings
        </Link>
      </div>
      
      <div className="sessions-container">
        <div className="sessions-info-group">
          <h2>Session Management</h2>
          <div className="info-description">
            Manage your active sessions across different devices and browsers. 
            You can view all your current sessions and revoke access from devices you no longer use.
          </div>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
            <button onClick={fetchSessions} className="retry-button">
              Retry
            </button>
          </div>
        )}

        {sessions.length === 0 ? (
          <div className="no-sessions">
            <p>No active sessions found.</p>
          </div>
        ) : (
          <div className="sessions-list">
            {sessions.map((session) => (
              <div key={session.id} className={`session-item ${session.is_current ? 'current-session' : ''}`}>
                <div className="session-info">
                  <div className="session-header">
                    <span className="session-id">Session ID: {session.id.slice(0, 8)}...</span>
                    {session.is_current && (
                      <span className="current-badge">Current Session</span>
                    )}
                  </div>
                  <div className="session-details">
                    <p><strong>Created:</strong> {formatDate(session.created_at)}</p>
                    <p><strong>Expires:</strong> {formatDate(session.expire_at)}</p>
                  </div>
                </div>
                {!session.is_current && (
                  <button
                    onClick={() => revokeSession(session.id)}
                    className="revoke-button"
                  >
                    Revoke
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="sessions-actions">
          <button onClick={fetchSessions} className="refresh-button">
            Refresh Sessions
          </button>
          <Link to="/settings" className="settings-link-button">
            Back to Settings
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SessionsPage;