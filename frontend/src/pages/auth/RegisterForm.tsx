import { useState } from 'react';
import { AuthApi } from '../../client/api';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { UsernameStep, VerificationStep, PasswordStep } from './Register';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();

  const handleSendVerificationCode = async () => {
    if (!username.trim()) {
      setError(t('auth.pleaseEnterUsername'));
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
      setError(t('auth.failedToSendVerificationCode'));
    }
  };

  const handleVerifyCode = async () => {
    if (!verificationCode.trim()) {
      setError(t('auth.pleaseEnterVerificationCode'));
      return;
    }

    setError('');

    try {
      const authApi = createAuthenticatedClient(AuthApi);
      const response = await authApi.verifyCodeApiAuthVerifyCodePost( { username: username.trim(), code: verificationCode.trim() });
      
      if (response.data.success) {
        setCurrentStep('password');
      } else {
        setError(response.data.message || t('auth.invalidVerificationCode'));
      }
    } catch (err: any) {
      setError(t('auth.failedToVerifyCode'));
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError(t('auth.passwordsDoNotMatch'));
      return;
    }

    try {
      const authApi = createAuthenticatedClient(AuthApi);
      const response = await authApi.registerApiAuthRegisterPost( { username: username.trim(), password, verification_code: verificationCode.trim() });
      
      if (response.status === 200) {
        onSuccess();
      }
    } catch (err: any) {
      setError(t('auth.registrationFailed'));
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