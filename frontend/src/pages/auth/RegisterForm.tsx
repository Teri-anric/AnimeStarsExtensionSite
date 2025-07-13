import { useState } from 'react';
import { AuthApi } from '../../client/api';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { UsernameStep, VerificationStep, PasswordStep } from './Register';

interface RegisterFormProps {
  onSuccess: () => void;
}

type RegistrationStep = 'username' | 'verification' | 'password';

const RegisterForm = ({ onSuccess }: RegisterFormProps) => {
  const [currentStep, setCurrentStep] = useState<RegistrationStep>('username');
  const [username, setUsername] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSendVerificationCode = async () => {
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    setError('');

    try {
      const authApi = createAuthenticatedClient(AuthApi);
      const response = await authApi.sendVerificationCodeApiAuthSendVerificationPost( { username: username.trim() });
      
      if (response.status === 200) {
        setCurrentStep('verification');
      }
    } catch (err: any) {
      setError('Failed to send verification code. Please try again.');
    }
  };

  const handleVerifyCode = async () => {
    if (!verificationCode.trim()) {
      setError('Please enter the verification code');
      return;
    }

    setError('');

    try {
      const authApi = createAuthenticatedClient(AuthApi);
      const response = await authApi.verifyCodeApiAuthVerifyCodePost( { username: username.trim(), code: verificationCode.trim() });
      
      if (response.data.success) {
        setCurrentStep('password');
      } else {
        setError(response.data.message || 'Invalid verification code');
      }
    } catch (err: any) {
      setError('Failed to verify code. Please try again.');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const authApi = createAuthenticatedClient(AuthApi);
      const response = await authApi.registerApiAuthRegisterPost( { username: username.trim(), password, verification_code: verificationCode.trim() });
      
      if (response.status === 200) {
        onSuccess();
      }
    } catch (err: any) {
      setError('Registration failed. Please try again.');
    }
  };

  const handleBackToUsername = () => {
    setCurrentStep('username');
    setVerificationCode('');
    setError('');
  };

  const handleBackToVerification = () => {
    setCurrentStep('verification');
    setPassword('');
    setConfirmPassword('');
    setError('');
  };

  return (
    <div className="register-form">
      {currentStep === 'username' && (
        <UsernameStep
          username={username}
          error={error}
          onUsernameChange={setUsername}
          onSendVerificationCode={handleSendVerificationCode}
        />
      )}
      
      {currentStep === 'verification' && (
        <VerificationStep
          username={username}
          verificationCode={verificationCode}
          error={error}
          onVerificationCodeChange={setVerificationCode}
          onVerifyCode={handleVerifyCode}
          onBackToUsername={handleBackToUsername}
        />
      )}
      
      {currentStep === 'password' && (
        <PasswordStep
          username={username}
          password={password}
          confirmPassword={confirmPassword}
          error={error}
          onPasswordChange={setPassword}
          onConfirmPasswordChange={setConfirmPassword}
          onSubmit={handleRegister}
          onBackToVerification={handleBackToVerification}
        />
      )}
    </div>
  );
};

export default RegisterForm; 