// frontend/src/pages/ChatPage.js
import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../contexts/AuthContext'; // 用于登出等
import { Link } from 'react-router-dom';

function ChatPage() {
    const [currentUserDetails, setCurrentUserDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { userId, logout } = useContext(AuthContext); // 从 AuthContext 获取 userId 和 logout

    useEffect(() => {
        const fetchUserDetails = async () => {
            if (!userId) { // 如果 AuthContext 中还没有 userId，则不执行
                setIsLoading(false); // 或者可以等待 userId 可用
                return;
            }
            setIsLoading(true);
            try {
                // 使用 /api/auth/me 获取当前登录用户的信息
                // 这个接口会通过token自动识别用户
                const response = await axios.get('http://localhost:5001/api/auth/me');
                setCurrentUserDetails(response.data);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch user details for chat:', err);
                setError(err.response?.data?.msg || 'Could not load user data.');
                if (err.response?.status === 401 || err.response?.status === 422) {
                    // Token 可能已失效
                    logout(); // 执行登出清除token
                }
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserDetails();
    }, [userId, logout]); // 当 userId 变化时重新获取 (虽然登录后 userId 不应变化，但这是好的依赖)

    if (isLoading) {
        return <div>Loading chat user data...</div>;
    }

    if (error) {
        return <div>Error: {error} <button onClick={() => window.location.reload()}>Try again</button></div>;
    }

    if (!currentUserDetails) {
        return <div>User data not available. You might be logged out.</div>;
    }

    return (
        <div>
            <header style={{ padding: '1rem', background: '#f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>KaguChat - Welcome, {currentUserDetails.nickname || currentUserDetails.username}!</h1>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    {currentUserDetails.avatar_url && <img src={currentUserDetails.avatar_url} alt="avatar" style={{ width: 40, height: 40, borderRadius: '50%', marginRight: '1rem' }} />}
                    {/* 添加 Admin Panel 入口 */}
                    <Link to="/admin" style={{ marginRight: '1rem', padding: '0.5rem 1rem', background: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
                        Admin Panel
                    </Link>
                    <button onClick={logout} style={{ padding: '0.5rem 1rem', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                        Logout
                    </button>
                </div>
            </header>
            <main>
                <p>Chat content goes here...</p>
                <p>Your User ID: {currentUserDetails.user_id}</p>
                {/* 在这里构建聊天界面的其他部分，如联系人列表、消息区域等 */}
            </main>
        </div>
    );
}

export default ChatPage;