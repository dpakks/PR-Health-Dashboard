import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { verifyForgotOTP } from "../services/authService";

const OTP_LENGTH = 6;

function ForgotVerifyOTP() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email;

  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRefs = useRef([]);

  useEffect(() => {
    if (!email) {
      navigate("/forgot-password");
    }
  }, [email, navigate]);

  const handleChange = (index, value) => {
    if (!/^\d?$/.test(value)) return;

    const updated = [...otp];
    updated[index] = value;
    setOtp(updated);
    setError("");

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
      const data = await verifyForgotOTP(email, otpString);

      // OTP verified — navigate to reset password with reset token
      navigate("/reset-password", {
        state: { resetToken: data.reset_token },
      });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Invalid or expired OTP");
      setOtp(Array(OTP_LENGTH).fill(""));
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
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
          {loading ? "Verifying..." : "Verify Code"}
        </button>
      </form>

      <div className="otp-footer">
        <span
          className="back-to-login"
          onClick={() => navigate("/forgot-password")}
        >
          ← Back
        </span>
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default ForgotVerifyOTP;