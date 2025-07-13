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
  return (
    <div className="register-step">
      <h2>Step 2: Enter Verification Code</h2>
      <p>We've sent a verification code to your Animestar account via private message.</p>
      <p><strong>Username:</strong> {username}</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="verification-code">Verification Code</label>
        <input
          type="text"
          id="verification-code"
          value={verificationCode}
          onChange={(e) => onVerificationCodeChange(e.target.value)}
          placeholder="Enter 6-digit code"
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
          Back
        </button>
        <button 
          type="button" 
          onClick={onVerifyCode}
          disabled={!verificationCode.trim()} 
          className="submit-button"
        >
          Verify Code
        </button>
      </div>
    </div>
  );
};

export default VerificationStep; 