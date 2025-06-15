import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import RegisterForm from './RegisterForm';

const RegisterPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

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
          Already have an account?{' '}
          <Link to="/login" className="text-button">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage; 