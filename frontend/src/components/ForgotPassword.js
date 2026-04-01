import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { forgotPassword } from "../services/authService";

function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await forgotPassword(email);

      // OTP sent — navigate to verification
      navigate("/forgot-verify-otp", { state: { email: data.email } });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-title">Forgot Password</h2>
      <p className="login-subtitle">
        Enter your registered email address and we'll send you a verification
        code
      </p>

      <form className="login-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Sending OTP..." : "Send Verification Code"}
        </button>
      </form>

      <div className="login-links">
        <span className="back-to-login" onClick={() => navigate("/")}>
          ← Back to Login
        </span>
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default ForgotPassword;