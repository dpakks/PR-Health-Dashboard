import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Projects from "./components/Projects";
import Users from "./components/Users";
import DashboardLayout from "./components/DashboardLayout";
import "./App.css";

function App() {
  const role = localStorage.getItem("role"); // ADMIN or TECH_LEAD

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route
          path="/projects"
          element={
            <DashboardLayout role={role}>
              <Projects />
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
