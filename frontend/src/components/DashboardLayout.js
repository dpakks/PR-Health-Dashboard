import React, { useEffect, useState } from "react";
import Sidebar from "./Sidebar";

function DashboardLayout({ role, children }) {
  const [collapsed, setCollapsed] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 820);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 820;
      setIsMobile(mobile);

      if (!mobile) {
        setMobileOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="layout">
      {isMobile && !mobileOpen && (
        <button
          className="mobile-menu-trigger"
          onClick={() => setMobileOpen(true)}
          aria-label="Open menu"
        >
          ☰
        </button>
      )}

      <Sidebar
        role={role}
        collapsed={collapsed}
        toggle={() => setCollapsed(!collapsed)}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        isMobile={isMobile}
      />

      <div className="page-content">{children}</div>
    </div>
  );
}

export default DashboardLayout;