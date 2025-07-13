import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';
import RegisterForm from './RegisterForm';

const RegisterPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleRegisterSuccess = () => {
    navigate('/login');
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <RegisterForm onSuccess={handleRegisterSuccess} />
        <p className="auth-toggle">
          {t('registerPage.hasAccount')}{' '}
          <Link to="/login" className="text-button">
            {t('registerPage.login')}
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage; 