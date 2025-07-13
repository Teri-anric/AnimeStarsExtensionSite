import React from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/LanguageSwitcher.css';

const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();

  const languages = [
    { code: 'en', name: t('languageSwitcher.english'), flag: '🇺🇸' },
    { code: 'uk', name: t('languageSwitcher.ukrainian'), flag: '🇺🇦' },
    { code: 'ru', name: t('languageSwitcher.russian'), flag: '🇷🇺' }
  ];

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
  };

  return (
    <div className="language-switcher">
      <div className="language-dropdown">
        <button className="language-button">
          <span className="current-flag">
            {languages.find(lang => lang.code === i18n.language)?.flag || '🌐'}
          </span>
          <span className="current-language">
            {languages.find(lang => lang.code === i18n.language)?.name || t('languageSwitcher.language')}
          </span>
          <span className="dropdown-arrow">▼</span>
        </button>
        
        <div className="language-options">
          {languages.map((language) => (
            <button
              key={language.code}
              className={`language-option ${i18n.language === language.code ? 'active' : ''}`}
              onClick={() => handleLanguageChange(language.code)}
            >
              <span className="flag">{language.flag}</span>
              <span className="name">{language.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LanguageSwitcher;