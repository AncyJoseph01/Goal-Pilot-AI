import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = ({ children, unreadCount, showNotifications, toggleNotifications }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

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
      <div className={`sidebar-container ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Sidebar />
        <button 
          className="sidebar-toggle"
          onClick={toggleSidebar}
        >
          {sidebarCollapsed ? '➡️' : '⬅️'}
        </button>
      </div>

      {!sidebarCollapsed && isMobile && (
        <div 
          className="sidebar-overlay"
          onClick={closeSidebar}
        />
      )}

      <div className={`main-content ${sidebarCollapsed ? 'expanded' : ''}`}>
        <Header
          unreadCount={unreadCount}
          showNotifications={showNotifications}
          toggleNotifications={toggleNotifications}
        />
        <main className="content" onClick={closeSidebar}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;