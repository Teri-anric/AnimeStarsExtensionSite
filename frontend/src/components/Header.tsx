import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import '../styles/Header.css';

const Header = () => {
  const { isAuthenticated, username, logout } = useAuth();
  const { t } = useTranslation();

  return (
    <header className="app-header">
      <div className="header-logo">
        <Link to="/">{t('header.logo')}</Link>
      </div>
      
      {isAuthenticated && (
        <nav className="main-nav">
          <NavLink to="/cards" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            {t('navigation.cards')}
          </NavLink>
          <NavLink to="/decks" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            {t('navigation.decks')}
          </NavLink>
          <NavLink to="/random-gif" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            {t('navigation.randomGif')}
          </NavLink>
          <NavLink to="/fqa" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            {t('navigation.fqa')}
          </NavLink>
        </nav>
      )}
      
      <nav className="user-nav">
        {isAuthenticated ? (
          <div className="user-menu">
            <span className="username">{t('auth.welcomeUser', { username })}</span>
            <div className="user-actions">
              <Link to="/settings" className="settings-link">
                {t('common.settings')}
              </Link>
              <button className="logout-button" onClick={logout}>
                {t('auth.logout')}
              </button>
            </div>
          </div>
        ) : (
          <div className="user-menu">
            <LanguageSwitcher />
            <NavLink to="/fqa" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              {t('navigation.fqa')}
            </NavLink>
            <Link to="/login" className="login-button">
              {t('auth.login')}
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header; 