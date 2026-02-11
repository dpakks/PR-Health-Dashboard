import React from "react";
import { useNavigate } from "react-router-dom";

function Sidebar({ collapsed, toggle }) {
  const navigate = useNavigate();
  const role = localStorage.getItem("role");

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : "expanded"}`}>
      <div className="sidebar-header">
        <button className="hamburger" onClick={toggle}>☰</button>
      </div>

      <ul className="sidebar-menu">
        {role === "ADMIN" && (
          <li onClick={() => navigate("/users")}>
            👤 {!collapsed && "Users"}
          </li>
        )}

        <li onClick={() => navigate("/projects")}>
          📁 {!collapsed && "Projects"}
        </li>
      </ul>

      <div className="sidebar-footer" onClick={handleLogout}>
        ⎋ {!collapsed && "Logout"}
      </div>
    </div>
  );
}

export default Sidebar;
