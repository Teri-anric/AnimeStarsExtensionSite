import ExtensionStatus from '../../components/ExtensionStatus';
import '../../styles/settings/ExtensionSettings.css';

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
        <h3>Installation</h3>
        <div className="installation-steps">
          <div className="step">
            <span className="step-number">1</span>
            <div className="step-content">
              <h4>Download Extension</h4>
              <p>Download the Anime Stars browser extension from the Chrome Web Store or GitHub releases.</p>
              <div className="download-buttons">
                <a 
                  href="https://chromewebstore.google.com/detail/animestar-extension/ocpbplnohadkjdindnodcmpmjboifjae" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="download-button chrome-store-button"
                >
                  <img src="/icons/chrome_web_store.ico" alt="Chrome Web Store" className="button-icon" />
                  <span>Chrome Web Store</span>
                </a>
                <a 
                  href="https://github.com/Teri-anric/AnimeStarsExtensions/releases/latest" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="download-button github-button"
                >
                  <img src="/github-mark/github-mark-white.svg" alt="GitHub" className="button-icon" />
                  <span>GitHub (Firefox XPI)</span>
                </a>
              </div>
            </div>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <div className="step-content">
              <h4>Install Extension</h4>
              <p>For Chrome: Follow the installation instructions in the Chrome Web Store. For Firefox: Download the XPI file from GitHub and install it manually.</p>
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