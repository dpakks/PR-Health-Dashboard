import React, { useState } from "react";
import Sidebar from "./Sidebar";

function DashboardLayout({ role, children }) {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <div className="layout">
      <Sidebar
        role={role}
        collapsed={collapsed}
        toggle={() => setCollapsed(!collapsed)}
      />

      <div className="page-content">
        {children}
      </div>
    </div>
  );
}

export default DashboardLayout;
