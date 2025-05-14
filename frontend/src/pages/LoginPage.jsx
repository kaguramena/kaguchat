// frontend/src/pages/LoginPage.js
import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext'; // 确保路径正确

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    const navigate = useNavigate();
    const auth = useContext(AuthContext);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoggingIn(true);
        const result = await auth.login(username, password);
        setIsLoggingIn(false);
        if (result.success) {
            navigate('/chat'); // 或其他目标页面
        } else {
            setError(result.error || 'Invalid username or password.');
        }
    };
    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'linear-gradient(to right, #6EE7B7, #3B82F6)' }}>
            <div style={{ background: 'white', padding: '40px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' }}>
                <h2 style={{ textAlign: 'center', color: '#10B981', marginBottom: '24px', fontSize: '2rem', fontWeight: 'bold' }}>KaguChat</h2>
                {error && <p style={{ color: 'red', textAlign: 'center', marginBottom: '16px' }}>{error}</p>}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', color: '#374151', marginBottom: '8px' }}>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{ width: '100%', padding: '12px', border: '1px solid #D1D5DB', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="Enter your username"
                            disabled={isLoggingIn}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', color: '#374151', marginBottom: '8px' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ width: '100%', padding: '12px', border: '1px solid #D1D5DB', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="Enter your password"
                            disabled={isLoggingIn}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        style={{ width: '100%', background: '#10B981', color: 'white', padding: '12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontSize: '1rem', opacity: isLoggingIn ? 0.7 : 1 }}
                        disabled={isLoggingIn}
                    >
                        {isLoggingIn ? 'Logging in...' : 'Login'}
                    </button>
                    <p style={{ textAlign: 'center', marginTop: '16px' }}>
                        Don't have an account? <a href="/signup" style={{ color: '#3B82F6', textDecoration: 'none' }}>Sign Up</a>
                    </p>
                </form>
            </div>
        </div>
    );
}

export default LoginPage;