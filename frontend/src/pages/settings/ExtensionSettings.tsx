import { useTranslation } from 'react-i18next';
import ExtensionStatus from '../../components/ExtensionStatus';
import '../../styles/settings/ExtensionSettings.css';

const ExtensionSettings = () => {
  const { t } = useTranslation();
  
  return (
    <div className="extension-settings-content">
      <div className="settings-section">
        <h2>{t('settings.browserExtension')}</h2>
        <div className="setting-description">
          {t('settings.extensionDescription')}
        </div>
        <ExtensionStatus />
      </div>
      
      <div className="settings-section">
        <h3>{t('settings.installation')}</h3>
        <div className="installation-steps">
          <div className="step">
            <span className="step-number">1</span>
            <div className="step-content">
              <h4>{t('settings.downloadExtension')}</h4>
              <p>{t('settings.downloadExtensionDescription')}</p>
              <div className="download-buttons">
                <a 
                  href="https://chromewebstore.google.com/detail/animestar-extension/ocpbplnohadkjdindnodcmpmjboifjae" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="download-button chrome-store-button"
                >
                  <img src="/icons/chrome_web_store.ico" alt="Chrome Web Store" className="button-icon" />
                  <span>{t('settings.chromeWebStore')}</span>
                </a>
                <a 
                  href="https://github.com/Teri-anric/AnimeStarsExtensions/releases/latest" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="download-button github-button"
                >
                  <img src="/github-mark/github-mark-white.svg" alt="GitHub" className="button-icon" />
                  <span>{t('settings.githubFirefoxXpi')}</span>
                </a>
              </div>
            </div>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <div className="step-content">
              <h4>{t('settings.installExtension')}</h4>
              <p>{t('settings.installExtensionDescription')}</p>
            </div>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <div className="step-content">
              <h4>{t('settings.connectAccount')}</h4>
              <p>{t('settings.connectAccountDescription')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtensionSettings;