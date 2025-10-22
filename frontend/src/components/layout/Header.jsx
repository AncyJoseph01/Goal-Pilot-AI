import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = ({ unreadCount, showNotifications, toggleNotifications, onSearch }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [theme, setTheme] = useState('light');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard':
        return 'Dashboard';
      case '/create-goal':
        return 'Create Goal';
      case '/':
        return 'Dashboard';
      default:
        return 'Goal Pilot AI';
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    navigate('/login');
  };

  // **SEARCH HANDLER**
  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (onSearch) {
      onSearch(term);  // ✅ PASS TO DASHBOARD
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h2>{getPageTitle()}</h2>
        </div>
        <div className="header-search">
          {/* ✅ SINGLE SEARCH BAR */}
          <input
            type="text"
            placeholder="Search goals, resources..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
        <div className="header-actions">
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <div className="notifications-bell" onClick={toggleNotifications}>
            🔔 {unreadCount > 0 && <span className="notification-count">{unreadCount}</span>}
          </div>
          <div className="avatar">U</div>
          <button onClick={handleLogout} className="btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;