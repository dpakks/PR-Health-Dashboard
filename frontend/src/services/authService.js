import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

// Step 1: Login — sends OTP to user's email
export const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/users/login`, {
    email,
    password,
  });
  return response.data;
};

// Step 2: Verify login OTP — returns JWT
export const verifyLoginOTP = async (email, otp) => {
  const response = await axios.post(`${API_URL}/users/verify-otp`, {
    email,
    otp,
  });
  return response.data;
};

// Forgot Password Step 1: Send OTP to email
export const forgotPassword = async (email) => {
  const response = await axios.post(`${API_URL}/users/forgot-password`, {
    email,
  });
  return response.data;
};

// Forgot Password Step 2: Verify OTP — returns reset token
export const verifyForgotOTP = async (email, otp) => {
  const response = await axios.post(`${API_URL}/users/verify-forgot-otp`, {
    email,
    otp,
  });
  return response.data;
};

// Forgot Password Step 3: Reset password using reset token
export const resetPassword = async (resetToken, newPassword) => {
  const response = await axios.post(`${API_URL}/users/reset-password`, {
    reset_token: resetToken,
    new_password: newPassword,
  });
  return response.data;
};