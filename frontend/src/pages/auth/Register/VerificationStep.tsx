import { useTranslation } from 'react-i18next';

interface VerificationStepProps {
  username: string;
  verificationCode: string;
  error: string;
  onVerificationCodeChange: (code: string) => void;
  onVerifyCode: () => void;
  onBackToUsername: () => void;
}

const VerificationStep = ({ 
  username, 
  verificationCode, 
  error, 
  onVerificationCodeChange, 
  onVerifyCode, 
  onBackToUsername 
}: VerificationStepProps) => {
  const { t } = useTranslation();
  
  return (
    <div className="register-step">
      <h2>{t('registration.step2Title')}</h2>
      <p>{t('registration.step2Description')}</p>
      <p><strong>{t('auth.username')}:</strong> {username}</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="verification-code">{t('verificationStep.verificationCode')}</label>
        <input
          type="text"
          id="verification-code"
          value={verificationCode}
          onChange={(e) => onVerificationCodeChange(e.target.value)}
          placeholder={t('registration.enterVerificationCode')}
          maxLength={6}
          required
        />
      </div>
      
      <div className="button-group">
        <button 
          type="button" 
          onClick={onBackToUsername}
          className="secondary-button"
        >
          {t('common.back')}
        </button>
        <button 
          type="button" 
          onClick={onVerifyCode}
          disabled={!verificationCode.trim()} 
          className="submit-button"
        >
          {t('registration.verifyCode')}
        </button>
      </div>
    </div>
  );
};

export default VerificationStep; 