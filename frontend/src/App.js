import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateGoal from './pages/CreateGoal';
import './App.css';
import GoogleSuccess from './pages/GoogleSuccess';

function App() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [authState, setAuthState] = useState(!!localStorage.getItem('token')); // Track auth state
  const location = useLocation(); // Track location changes

  // Disable notifications fetch until needed
  /* useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch('http://127.0.0.1:8000/users/notifications', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
        .then(response => response.json())
        .then(data => setNotifications(data))
        .catch(error => console.error('Error fetching notifications:', error));
    }
  }, []); */

  useEffect(() => {
  const token = localStorage.getItem('token');
  setAuthState(!!token);
}, [location]);

  const toggleNotifications = () => setShowNotifications(!showNotifications);

  const markNotificationAsRead = (id) => {
    setNotifications(notifications.map(notif =>
      notif.id === id ? { ...notif, is_read: true } : notif
    ));
  };

  // Check if user is authenticated
  const isAuthenticated = () => authState;

  return (
    <Routes>
      <Route 
        path="/login" 
        element={!isAuthenticated() ? <Login /> : <Navigate to="/dashboard" replace />} 
      />
      <Route 
        path="/" 
        element={<Navigate to="/login" replace />} // Default to login page
      />
      
      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          isAuthenticated() ? (
            <Layout
              unreadCount={unreadCount}
              showNotifications={showNotifications}
              toggleNotifications={toggleNotifications}
            >
              <Dashboard
                notifications={notifications}
                markNotificationAsRead={markNotificationAsRead}
              />
            </Layout>
          ) : <Navigate to="/login" replace />
        } 
      />
      
      <Route 
        path="/create-goal" 
        element={
          isAuthenticated() ? (
            <Layout
              unreadCount={unreadCount}
              showNotifications={showNotifications}
              toggleNotifications={toggleNotifications}
            >
              <CreateGoal />
            </Layout>
          ) : <Navigate to="/login" replace />
        } 
      />
      
      <Route path="*" element={<div>404 - Page Not Found</div>} />

      <Route 
  path="/google-success" 
  element={<GoogleSuccess setAuthState={setAuthState} />} 
/>
    </Routes>

    
  );
}

// Wrapper to handle Router context
const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);

export default AppWrapper;