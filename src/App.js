import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateGoal from './pages/CreateGoal';

import './App.css';

// Optional: Add route protection for authenticated routes
// const ProtectedRoute = ({ children }) => {
//   const isAuthenticated = true; // Replace with your auth logic
//   return isAuthenticated ? children : <Navigate to="/login" />;
// };

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <Layout>
              {/* <ProtectedRoute> */}
                <Dashboard />
              {/* </ProtectedRoute> */}
            </Layout>
          } 
        />
        
        <Route 
          path="/create-goal" 
          element={
            <Layout>
              {/* <ProtectedRoute> */}
                <CreateGoal />
              {/* </ProtectedRoute> */}
            </Layout>
          } 
        />
        
        {/* Optional: 404 Page */}
        <Route path="*" element={<div>404 - Page Not Found</div>} />
      </Routes>
    </Router>
  );
}

export default App;