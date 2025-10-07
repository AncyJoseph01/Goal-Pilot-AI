import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const closeSidebar = () => {
    if (isMobile) {
      setSidebarCollapsed(true);
    }
  };

  return (
    <div className="layout">
      {/* Sidebar with toggle functionality */}
      <div className={`sidebar-container ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Sidebar />
        
        {/* Sidebar Toggle Button */}
        <button 
          className="sidebar-toggle"
          onClick={toggleSidebar}
        >
          {sidebarCollapsed ? '➡️' : '⬅️'}
        </button>
      </div>

      {/* Overlay for mobile when sidebar is open */}
      {!sidebarCollapsed && isMobile && (
        <div 
          className="sidebar-overlay"
          onClick={closeSidebar}
        />
      )}

      {/* Main Content Area */}
      <div className={`main-content ${sidebarCollapsed ? 'expanded' : ''}`}>
        <Header />
        <main className="content" onClick={closeSidebar}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;