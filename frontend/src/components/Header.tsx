import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Header.css';

const Header = () => {
  const { isAuthenticated, username, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="header-logo">
        <Link to="/">Anime Stars</Link>
      </div>
      
      {isAuthenticated && (
        <nav className="main-nav">
          <NavLink to="/cards" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Cards
          </NavLink>
          <NavLink to="/decks" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Decks
          </NavLink>
          <NavLink to="/random-gif" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Random GIF
          </NavLink>
        </nav>
      )}
      
      <nav className="user-nav">
        {isAuthenticated ? (
          <div className="user-menu">
            <span className="username">Welcome, {username}</span>
            <div className="user-actions">
              <Link to="/settings" className="settings-link">
                Settings
              </Link>
              <button className="logout-button" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        ) : (
          <Link to="/login" className="login-button">
            Login
          </Link>
        )}
      </nav>
    </header>
  );
};

export default Header; 