import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoginForm from './LoginForm';

const LoginPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="auth-page">
      <div className="auth-container">
        <LoginForm />
        <p className="auth-toggle">
          Don't have an account?{' '}
          <Link to="/register" className="text-button">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage; 