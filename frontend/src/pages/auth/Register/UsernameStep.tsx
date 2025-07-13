interface UsernameStepProps {
  username: string;
  error: string;
  onUsernameChange: (username: string) => void;
  onSendVerificationCode: () => void;
}

const UsernameStep = ({ username, error, onUsernameChange, onSendVerificationCode }: UsernameStepProps) => {
  return (
    <div className="register-step">
      <h2>Step 1: Enter Your Username</h2>
      <p>Enter your username from the Animestars website to start registration. Please note that usernames are case-sensitive.</p>
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="reg-username">Username</label>
        <input
          type="text"
          id="reg-username"
          value={username}
          onChange={(e) => onUsernameChange(e.target.value)}
          placeholder="Enter your Animestar username"
          required
        />
      </div>
      
      <button 
        type="button" 
        onClick={onSendVerificationCode}
        disabled={!username.trim()} 
        className="submit-button"
      >
        Send Verification Code
      </button>
    </div>
  );
};

export default UsernameStep; 