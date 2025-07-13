import { useTranslation } from 'react-i18next';

interface UsernameStepProps {
  username: string;
  error: string;
  onUsernameChange: (username: string) => void;
  onSendVerificationCode: () => void;
}

const UsernameStep = ({ username, error, onUsernameChange, onSendVerificationCode }: UsernameStepProps) => {
  const { t } = useTranslation();
  
  return (
    <div className="register-step">
      <h2>{t('registration.step1Title')}</h2>
      <p>{t('registration.step1Description')}</p>
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="reg-username">{t('auth.username')}</label>
        <input
          type="text"
          id="reg-username"
          value={username}
          onChange={(e) => onUsernameChange(e.target.value)}
          placeholder={t('registration.enterUsername')}
          required
        />
      </div>
      
      <button 
        type="button" 
        onClick={onSendVerificationCode}
        disabled={!username.trim()} 
        className="submit-button"
      >
        {t('registration.sendVerificationCode')}
      </button>
    </div>
  );
};

export default UsernameStep; 