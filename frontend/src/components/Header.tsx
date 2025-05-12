import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { isAuthenticated, username, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="header-logo">
        <Link to="/">Anime Stars</Link>
      </div>
      
      <nav className="header-nav">
        {isAuthenticated ? (
          <div className="user-info">
            <span className="username">Welcome, {username}</span>
            <button className="logout-button" onClick={logout}>
              Logout
            </button>
          </div>
        ) : (
          <Link to="/auth" className="login-button">
            Login
          </Link>
        )}
      </nav>
    </header>
  );
};

export default Header; 