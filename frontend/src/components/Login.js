import { useNavigate } from "react-router-dom";
import { login } from "../services/authService";
import { useState } from "react";
import { jwtDecode } from "jwt-decode";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = await login(email, password);

      // ✅ Decode JWT properly
      const decoded = jwtDecode(data.access_token);

      // ✅ Store token & role
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", decoded.role);

      // 🚀 Redirect after login
      navigate("/projects");

    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-title">Log in</h2>
      <p className="login-subtitle">
        Enter your email and password to securely access your account
      </p>

      <form className="login-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Login</button>
      </form>

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default Login;
