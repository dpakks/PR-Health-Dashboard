import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { verifyLoginOTP } from "../services/authService";
import { jwtDecode } from "jwt-decode";

const OTP_LENGTH = 6;

function VerifyOTP() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email;

  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const inputRefs = useRef([]);

  // Redirect if no Email in state (direct URL access)
  useEffect(() => {
    if (!email) {
      navigate("/");
    }
  }, [email, navigate]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleChange = (index, value) => {
    if (!/^\d?$/.test(value)) return; // only digits

    const updated = [...otp];
    updated[index] = value;
    setOtp(updated);
    setError("");

    // Auto-focus next input
    if (value && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").trim();
    if (!/^\d+$/.test(pasted)) return;

    const digits = pasted.slice(0, OTP_LENGTH).split("");
    const updated = [...otp];
    digits.forEach((d, i) => {
      updated[i] = d;
    });
    setOtp(updated);

    const focusIndex = Math.min(digits.length, OTP_LENGTH - 1);
    inputRefs.current[focusIndex]?.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpString = otp.join("");

    if (otpString.length !== OTP_LENGTH) {
      setError("Please enter the full 6-digit OTP");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const data = await verifyLoginOTP(email, otpString);

      const decoded = jwtDecode(data.access_token);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", decoded.role);

      navigate("/projects");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Invalid or expired OTP");
      setOtp(Array(OTP_LENGTH).fill(""));
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setResending(true);
    setError("");

    try {
      // We don't have the password here, so we call login again
      // But we don't have it — so we use a dedicated resend approach
      // For now, inform the user to go back and login again
      setError("Please go back and login again to receive a new OTP");
    } catch (err) {
      setError("Failed to resend OTP. Please try again.");
    } finally {
      setResending(false);
      setResendCooldown(30);
    }
  };

  if (!email) return null;

  return (
    <div className="login-container">
      <h2 className="login-title">Verify OTP</h2>
      <p className="login-subtitle">
        We've sent a 6-digit code to <strong>{email}</strong>
      </p>

      <form className="login-form" onSubmit={handleSubmit}>
        <div className="otp-inputs" onPaste={handlePaste}>
          {otp.map((digit, i) => (
            <input
              key={i}
              ref={(el) => (inputRefs.current[i] = el)}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              className="otp-box"
              autoFocus={i === 0}
            />
          ))}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Verifying..." : "Verify & Login"}
        </button>
      </form>

      <div className="otp-footer">
        <span className="otp-footer-text">Didn't receive the code?</span>
        <span
          className={`resend-link ${resendCooldown > 0 ? "disabled" : ""}`}
          onClick={handleResend}
        >
          {resending
            ? "Sending..."
            : resendCooldown > 0
            ? `Resend in ${resendCooldown}s`
            : "Resend OTP"}
        </span>
      </div>

      <div className="otp-footer">
        <span className="back-to-login" onClick={() => navigate("/")}>
          ← Back to Login
        </span>
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default VerifyOTP;