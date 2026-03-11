import React from "react";
import { useNavigate } from "react-router-dom";
import { FolderIcon, UserIcon, LogoutIcon } from "../icons/Icons";

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
            <UserIcon /> {!collapsed && "Users"}
          </li>
        )}

        <li onClick={() => navigate("/projects")}>
          <FolderIcon /> {!collapsed && "Projects"}
        </li>
      </ul>

      <div className="sidebar-footer" onClick={handleLogout}>
        <LogoutIcon /> {!collapsed && "Logout"}
      </div>
    </div>
  );
}

export default Sidebar;
