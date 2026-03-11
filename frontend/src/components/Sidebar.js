import React from "react";
import { useNavigate } from "react-router-dom";
import { FolderIcon, UserIcon, LogoutIcon } from "../icons/Icons";

function Sidebar({ collapsed, toggle, mobileOpen, setMobileOpen, isMobile }) {
  const navigate = useNavigate();
  const role = localStorage.getItem("role");

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
    if (isMobile) setMobileOpen(false);
  };

  const handleNavigate = (path) => {
    navigate(path);
    if (isMobile) setMobileOpen(false);
  };

  if (isMobile) {
    return (
      <>
        {mobileOpen && (
          <div
            className="mobile-sidebar-backdrop"
            onClick={() => setMobileOpen(false)}
          />
        )}

        <div className={`mobile-sidebar ${mobileOpen ? "open" : ""}`}>
          <div className="mobile-sidebar-header">
            <h3 className="mobile-sidebar-title">Menu</h3>
            <button
              className="mobile-sidebar-close"
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu"
            >
              ✕
            </button>
          </div>

          <ul className="sidebar-menu">
            {role === "ADMIN" && (
              <li onClick={() => handleNavigate("/users")}>
                <UserIcon /> Users
              </li>
            )}

            <li onClick={() => handleNavigate("/projects")}>
              <FolderIcon /> Projects
            </li>
          </ul>

          <div className="sidebar-footer" onClick={handleLogout}>
            <LogoutIcon /> Logout
          </div>
        </div>
      </>
    );
  }

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : "expanded"}`}>
      <div className="sidebar-header">
        <button className="hamburger" onClick={toggle}>
          ☰
        </button>
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