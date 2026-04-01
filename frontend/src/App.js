import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import VerifyOTP from "./components/VerifyOTP";
import ForgotPassword from "./components/ForgotPassword";
import ForgotVerifyOTP from "./components/ForgotVerifyOTP";
import ResetPassword from "./components/ResetPassword";
import Projects from "./components/Projects";
import Users from "./components/Users";
import DashboardLayout from "./components/DashboardLayout";
import ProjectDashboard from "./components/ProjectDashboard";
import "./App.css";

function App() {
  const role = localStorage.getItem("role");

  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Flow */}
        <Route path="/" element={<Login />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/forgot-verify-otp" element={<ForgotVerifyOTP />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Dashboard */}
        <Route
          path="/projects"
          element={
            <DashboardLayout role={role}>
              <Projects />
            </DashboardLayout>
          }
        />
        <Route
          path="/projects/:id"
          element={
            <DashboardLayout role={role}>
              <ProjectDashboard />
            </DashboardLayout>
          }
        />
        <Route
          path="/users"
          element={
            <DashboardLayout role={role}>
              <Users />
            </DashboardLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;