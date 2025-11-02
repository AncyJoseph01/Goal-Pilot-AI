import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const GoogleSuccess = ({ setAuthState }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const email = params.get('email');
    const name = params.get('name');
    const token = params.get('token');

    if (email && token) {
      localStorage.setItem('token', token);
      localStorage.setItem('email', email);
      localStorage.setItem('name', name);
      setAuthState(true); // <-- update auth state in App.js
      navigate('/dashboard'); 
    } else {
      navigate('/login');
    }
  }, [navigate, setAuthState]);

  return <div>Logging you in...</div>;
};

export default GoogleSuccess;
