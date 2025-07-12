import ExtensionStatus from '../../components/ExtensionStatus';

const ExtensionSettings = () => {
  return (
    <div className="extension-settings-content">
      <div className="settings-section">
        <h2>Browser Extension</h2>
        <div className="setting-description">
          Connect the Anime Stars browser extension to sync your card statistics and get enhanced features.
        </div>
        <ExtensionStatus />
      </div>
      
      <div className="settings-section">
        <h3>Features</h3>
        <div className="feature-list">
          <div className="feature-item">
            <h4>Card Statistics Sync</h4>
            <p>Automatically sync your card collection and statistics across devices.</p>
          </div>
          <div className="feature-item">
            <h4>Enhanced Browsing</h4>
            <p>Get real-time information about anime cards while browsing.</p>
          </div>
          <div className="feature-item">
            <h4>Quick Actions</h4>
            <p>Access your favorite cards and decks directly from your browser.</p>
          </div>
        </div>
      </div>
      
      <div className="settings-section">
        <h3>Installation</h3>
        <div className="installation-steps">
          <div className="step">
            <span className="step-number">1</span>
            <div className="step-content">
              <h4>Download Extension</h4>
              <p>Download the Anime Stars browser extension from the Chrome Web Store or Firefox Add-ons.</p>
            </div>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <div className="step-content">
              <h4>Install Extension</h4>
              <p>Follow the installation instructions for your browser.</p>
            </div>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <div className="step-content">
              <h4>Connect Account</h4>
              <p>Use the extension token above to connect your account.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtensionSettings;