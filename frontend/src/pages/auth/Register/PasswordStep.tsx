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
  return (
    <div className="register-step">
      <h2>Step 3: Create Password</h2>
      <p>Create a password for your account.</p>
      <p><strong>Username:</strong> {username}</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={onSubmit}>
        <input name="username" value={username} style={{ display: 'none' }} />
        <div className="form-group">
          <label htmlFor="reg-password">Password</label>
          <input
            type="password"
            id="reg-password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => onConfirmPasswordChange(e.target.value)}
            placeholder="Confirm your password"
            required
          />
        </div>
        
        <div className="button-group">
          <button 
            type="button" 
            onClick={onBackToVerification}
            className="secondary-button"
          >
            Back
          </button>
          <button 
            type="submit" 
            className="submit-button"
          >
            Create Account
          </button>
        </div>
      </form>
    </div>
  );
};

export default PasswordStep; 