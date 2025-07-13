import { useTranslation } from 'react-i18next';

interface PasswordStepProps {
  username: string;
  password: string;
  confirmPassword: string;
  error: string;
  onPasswordChange: (password: string) => void;
  onConfirmPasswordChange: (password: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onBackToVerification: () => void;
}

const PasswordStep = ({ 
  username, 
  password, 
  confirmPassword, 
  error, 
  onPasswordChange, 
  onConfirmPasswordChange, 
  onSubmit, 
  onBackToVerification 
}: PasswordStepProps) => {
  const { t } = useTranslation();
  
  return (
    <div className="register-step">
      <h2>{t('registration.step3Title')}</h2>
      <p>{t('registration.step3Description')}</p>
      <p><strong>{t('auth.username')}:</strong> {username}</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={onSubmit}>
        <input name="username" value={username} style={{ display: 'none' }} />
        <div className="form-group">
          <label htmlFor="reg-password">{t('auth.password')}</label>
          <input
            type="password"
            id="reg-password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            placeholder={t('registration.enterPassword')}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirm-password">{t('auth.confirmPassword')}</label>
          <input
            type="password"
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => onConfirmPasswordChange(e.target.value)}
            placeholder={t('registration.confirmPassword')}
            required
          />
        </div>
        
        <div className="button-group">
          <button 
            type="button" 
            onClick={onBackToVerification}
            className="secondary-button"
          >
            {t('common.back')}
          </button>
          <button 
            type="submit" 
            className="submit-button"
          >
            {t('registration.createAccount')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PasswordStep; 