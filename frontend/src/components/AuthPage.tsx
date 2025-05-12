import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  
  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
  };
  
  const handleRegisterSuccess = () => {
    setIsLogin(true);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        {isLogin ? (
          <>
            <LoginForm />
            <p className="auth-toggle">
              Don't have an account?{' '}
              <button 
                className="text-button" 
                onClick={toggleAuthMode}
              >
                Register
              </button>
            </p>
          </>
        ) : (
          <>
            <RegisterForm onSuccess={handleRegisterSuccess} />
            <p className="auth-toggle">
              Already have an account?{' '}
              <button 
                className="text-button" 
                onClick={toggleAuthMode}
              >
                Login
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthPage; 