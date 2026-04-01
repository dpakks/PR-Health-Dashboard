import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { resetPassword } from "../services/authService";
import { jwtDecode } from "jwt-decode";

function ResetPassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const resetToken = location.state?.resetToken;

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!resetToken) {
      navigate("/forgot-password");
    }
  }, [resetToken, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const newErrors = {};

    if (!newPassword.trim()) {
      newErrors.newPassword = "This field is required";
    } else if (newPassword.length < 6) {
      newErrors.newPassword = "Password must be at least 6 characters";
    }

    if (!confirmPassword.trim()) {
      newErrors.confirmPassword = "This field is required";
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setLoading(true);

    try {
      const data = await resetPassword(resetToken, newPassword);

      // Password reset successful — user is auto-logged in
      const decoded = jwtDecode(data.access_token);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", decoded.role);

      navigate("/projects");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Failed to reset password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!resetToken) return null;

  return (
    <div className="login-container">
      <h2 className="login-title">Reset Password</h2>
      <p className="login-subtitle">
        Create a new password for your account
      </p>

      <form className="login-form" onSubmit={handleSubmit}>
        <div>
          <input
            type="password"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              setErrors((prev) => ({ ...prev, newPassword: "" }));
            }}
            className={errors.newPassword ? "input-error" : ""}
          />
          {errors.newPassword && (
            <div className="field-error">{errors.newPassword}</div>
          )}
        </div>

        <div>
          <input
            type="password"
            placeholder="Confirm new password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setErrors((prev) => ({ ...prev, confirmPassword: "" }));
            }}
            className={errors.confirmPassword ? "input-error" : ""}
          />
          {errors.confirmPassword && (
            <div className="field-error">{errors.confirmPassword}</div>
          )}
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Resetting..." : "Reset Password & Login"}
        </button>
      </form>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default ResetPassword;