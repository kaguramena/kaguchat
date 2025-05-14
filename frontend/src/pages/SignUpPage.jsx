import {react, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {AuthContext} from '../contexts/AuthContext'; // 确保路径正确
import axios from 'axios';
import { Link } from 'react-router-dom';

function SignUpPage(){
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [phone, setPhone] = useState('');
    const [avatar_url, setAvatarUrl] = useState('');
    const [nickname, setNickname] = useState('');
    
    // State 
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();
    // const auth = useContext(AuthContext); // 如果注册后自动登录，则需要

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        if(password !== confirmPassword){
            setError('Passwords do not match.');
            return;
        }
        if (phone.length !== 11 || !/^\d+$/.test(phone)) {
            setError("Phone number must be 11 digits.");
            return;
        }
        setIsSubmitting(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, {
                username,
                password,
                phone,
                nickname: nickname || username, // 如果昵称为空，则使用用户名
                avatar_url: avatar_url || null,
            });

            if (response.status === 201) {
                setSuccessMessage(response.data.msg || "Registration successful! Please log in.");
                // 清空表单
                setUsername('');
                setPassword('');
                setConfirmPassword('');
                setPhone('');
                setNickname('');
                // 可选：几秒后导航到登录页面
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                // 对于非201的成功响应（理论上不应该，但以防万一）
                setError(response.data.msg || "An unexpected response occurred.");
            }
        } catch (err) {
            if (err.response && err.response.data && err.response.data.msg) {
                setError(err.response.data.msg);
            } else {
                setError("Registration failed. Please try again later.");
            }
            console.error("Signup error:", err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: 'linear-gradient(to right, #3B82F6, #10B981 )', padding: '20px 0' }}>
            <div style={{ background: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', width: '100%', maxWidth: '450px' }}>
                <h2 style={{ textAlign: 'center', color: '#10B981', marginBottom: '24px', fontSize: '2rem', fontWeight: 'bold' }}>Create KaguChat Account</h2>
                
                {error && <p style={{ color: 'red', textAlign: 'center', marginBottom: '16px', background: '#ffebee', padding: '8px', borderRadius: '4px' }}>{error}</p>}
                {successMessage && <p style={{ color: 'green', textAlign: 'center', marginBottom: '16px', background: '#e8f5e9', padding: '8px', borderRadius: '4px' }}>{successMessage}</p>}
                
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Username<span style={{color: 'red'}}>*</span></label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="Choose a username"
                            disabled={isSubmitting}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Password<span style={{color: 'red'}}>*</span></label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="Create a password"
                            disabled={isSubmitting}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Confirm Password<span style={{color: 'red'}}>*</span></label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="Confirm your password"
                            disabled={isSubmitting}
                            required
                        />
                    </div>
                     <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Phone Number<span style={{color: 'red'}}>*</span></label>
                        <input
                            type="tel"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="11-digit phone number"
                            disabled={isSubmitting}
                            required
                            pattern="\d{11}"
                            title="Phone number must be 11 digits."
                        />
                    </div>
                     <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Nickname (Optional)</label>
                        <input
                            type="text"
                            value={nickname}
                            onChange={(e) => setNickname(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            placeholder="How should we call you?"
                            disabled={isSubmitting}
                        />
                    </div>
                    <button
                        type="submit"
                        style={{ width: '100%', background: '#10B981', color: 'white', padding: '12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontSize: '1rem', opacity: isSubmitting ? 0.7 : 1, transition: 'opacity 0.2s' }}
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Creating Account...' : 'Sign Up'}
                    </button>
                </form>
                <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.9rem' }}>
                    Already have an account? <Link to="/login" style={{ color: '#10B981', textDecoration: 'underline' }}>Log In</Link>
                </p>
            </div>
        </div>
    );

}

export default SignUpPage;