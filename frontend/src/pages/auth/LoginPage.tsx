import { useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';
import LoginForm from './LoginForm';

const LoginPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();

  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="auth-page">
      <div className="auth-container">
        <LoginForm />
        <p className="auth-toggle">
          {t('loginPage.noAccount')}{' '}
          <Link to="/register" className="text-button">
            {t('loginPage.register')}
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage; 