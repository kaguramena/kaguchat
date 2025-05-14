// frontend/src/pages/SignUpPage.jsx
import React, { useState, useContext } from 'react'; // 移除了 react (因为 React 自动导入)
import { useNavigate, Link } from 'react-router-dom'; // 确保 Link 已导入
import axios from 'axios';
// import { AuthContext } from '../contexts/AuthContext'; // 如果注册后自动登录或需要token

function SignUpPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [phone, setPhone] = useState('');
    const [nickname, setNickname] = useState('');
    const [avatarFile, setAvatarFile] = useState(null); // 用于存储文件对象
    const [avatarPreview, setAvatarPreview] = useState(''); // 用于预览图片

    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const handleAvatarChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > (16 * 1024 * 1024)) { // 假设最大 16MB
                setError('File is too large. Maximum size is 16MB.');
                setAvatarFile(null);
                setAvatarPreview('');
                e.target.value = null; // 清除文件输入
                return;
            }
            const allowedTypes = ['image/png', 'image/jpeg', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                setError('Invalid file type. Only PNG, JPG, GIF are allowed.');
                setAvatarFile(null);
                setAvatarPreview('');
                e.target.value = null; // 清除文件输入
                return;
            }
            setError(''); // 清除之前的错误
            setAvatarFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarPreview(reader.result);
            };
            reader.readAsDataURL(file);
        } else {
            setAvatarFile(null);
            setAvatarPreview('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (phone.length !== 11 || !/^\d+$/.test(phone)) {
            setError("Phone number must be 11 digits.");
            return;
        }
        setIsSubmitting(true);

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('phone', phone);
        formData.append('nickname', nickname || username);
        if (avatarFile) {
            formData.append('avatar', avatarFile);
        }

        try {
            // 发送 multipart/form-data
            const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    // 如果你的 signup 接口不需要 JWT Token (因为是公开注册)，则不需要 Authorization
                },
            });

            if (response.status === 201) {
                setSuccessMessage(response.data.msg || "Registration successful!");
                // 清空表单
                setUsername('');
                setPassword('');
                setConfirmPassword('');
                setPhone('');
                setNickname('');
                setAvatarFile(null);
                setAvatarPreview('');

                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
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
                    {/* ... (username, password, confirmPassword, phone, nickname input fields as before) ... */}
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
                            pattern="\d{11}" // HTML5 pattern validation
                            title="Phone number must be 11 digits."
                        />
                    </div>
                     <div style={{ marginBottom: '16px' }}> {/* Adjusted margin */}
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

                    <div style={{ marginBottom: '24px' }}> {/* Avatar input field */}
                        <label style={{ display: 'block', color: '#4A5568', marginBottom: '6px', fontSize: '0.9rem' }}>Avatar (Optional)</label>
                        <input
                            type="file"
                            onChange={handleAvatarChange}
                            accept="image/png, image/jpeg, image/gif"
                            style={{ width: '100%', padding: '10px', border: '1px solid #CBD5E0', borderRadius: '4px', boxSizing: 'border-box' }}
                            disabled={isSubmitting}
                        />
                        {avatarPreview && (
                            <div style={{ marginTop: '10px', textAlign: 'center' }}>
                                <img src={avatarPreview} alt="Avatar Preview" style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #10B981' }} />
                            </div>
                        )}
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