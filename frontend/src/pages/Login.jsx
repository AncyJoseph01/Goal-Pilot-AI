import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(''); // New state for error message
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous error on new attempt
    try {
      const response = await fetch('http://127.0.0.1:8000/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      console.log('Response:', response, 'Data:', data);

      if (response.ok) {
        localStorage.setItem('token', data.id || data.email); // Placeholder until token is added
        navigate('/dashboard');
      } else {
        // const errorMsg = data.detail?.[0]?.msg || data.detail || 'Login failed. Please try again.';
        const errorMsg = data.detail?.[0]?.loc?.includes('email')
          ? 'Incorrect email'
          : data.detail?.[0]?.loc?.includes('password')
            ? 'Incorrect password'
            : data.detail?.[0]?.msg || 'Login failed. Please try again.';
        setError(errorMsg);
        // setError(errorMsg); // Set error message from backend
        console.log('Error Detail:', data.detail);
      }
    } catch (error) {
      console.error('Error during login:', error);
      setError('An error occurred. Please check your network or server.');
    }
  };

  // Clear error when inputs change
  const handleInputChange = () => {
    if (error) setError('');
  };

  return (
    <div className="login-page">
      <div className="login-container glass-card">
        <h1>🚀 Goal Pilot AI</h1>
        <p>Your intelligent learning companion</p>

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => { setEmail(e.target.value); handleInputChange(); }}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); handleInputChange(); }}
            required
          />
          <button type="submit" className="btn-primary btn-large">Login</button>
          {error && <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
        </form>

        <p className="signup-link">
          Don't have an account? <a href="/signup">Sign up</a>
        </p>
      </div>
    </div>
  );
};

export default Login;