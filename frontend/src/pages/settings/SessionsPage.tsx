import { useState } from 'react';
import '../../styles/SessionsPage.css';

const SessionsPage = () => {
  const [loading] = useState(false);

  return (
    <div className="sessions-page">
      <div className="sessions-container">
        <h1>Active Sessions</h1>
        
        <div className="feature-coming-soon">
          <h2>🚧 Feature Coming Soon</h2>
          <p>
            The session management feature is currently being developed. 
            You will soon be able to:
          </p>
          <ul>
            <li>View all your active sessions</li>
            <li>See when each session was created and expires</li>
            <li>Revoke sessions from other devices</li>
            <li>Manage your account security</li>
          </ul>
          <p>
            <strong>Current Status:</strong> Backend API endpoints are being implemented.
          </p>
        </div>

        <div className="sessions-actions">
          <button 
            onClick={() => window.location.reload()} 
            className="refresh-button"
          >
            Refresh Page
          </button>
        </div>
      </div>
    </div>
  );
};

export default SessionsPage;