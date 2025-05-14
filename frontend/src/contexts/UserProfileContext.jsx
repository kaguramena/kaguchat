// frontend/src/contexts/UserProfileContext.js
import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import axios from 'axios';
import { AuthContext } from './AuthContext'; // 假设 AuthContext 在同一目录下

export const UserProfileContext = createContext();

export const UserProfileProvider = ({ children }) => {
    const [profile, setProfile] = useState(null);
    const [isLoadingProfile, setIsLoadingProfile] = useState(false); // 初始可以是 true，如果一开始就加载
    const [profileError, setProfileError] = useState(null);
    const { token, logout } = useContext(AuthContext);

    const fetchProfile = useCallback(async () => {
        if (!token) {
            setProfile(null); // 如果没有 token，确保 profile 是 null
            setIsLoadingProfile(false);
            return;
        }
        setIsLoadingProfile(true);
        setProfileError(null);
        try {
            const response = await axios.get('http://localhost:5001/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    // 如果 X-CSRF-TOKEN 也需要，并且你已将其存储在 AuthContext 或 localStorage:
                    'X-CSRF-TOKEN': localStorage.getItem('csrfToken') // 或从 AuthContext 获取
                } // 这里必须要及时设置token， 否则会由于全局头没有设置完成导致 401
            });
            setProfile(response.data);
            console.log('[UserProfileContext] Profile fetched:', response.data);
        } catch (error) {
            console.error('[UserProfileContext] Failed to fetch profile:', error.response?.data || error.message);
            setProfileError(error.response?.data || { msg: 'Could not load profile.' });
            setProfile(null);
            // 如果获取 profile 失败是因为 token 无效 (例如401, 422)，则执行登出
            if (error.response && (error.response.status === 401 || error.response.status === 422)) {
                console.warn('[UserProfileContext] Token invalid or expired while fetching profile. Logging out.');
                logout(); // 调用 AuthContext 的 logout
            }
        } finally {
            setIsLoadingProfile(false);
        }
    }, [token, logout]);

    useEffect(() => {
        // 当 token 存在 (即用户已登录或 token 从 localStorage 加载并验证后) 时，获取用户 profile
        // AuthContext 的 isLoadingAuth 状态可以用来判断初始 token 验证是否完成
        if (token) { // 只有当 token 确定有效时才获取
            fetchProfile();
        } else {
            // 如果没有 token (例如用户登出或初始加载时就没有有效 token)，清除 profile
            setProfile(null);
            setIsLoadingProfile(false); // 确保加载状态结束
        }
    }, [token, fetchProfile]); // 依赖 token 和 fetchProfile

    return (
        <UserProfileContext.Provider value={{ profile, isLoadingProfile, profileError, fetchProfile }}>
            {children}
        </UserProfileContext.Provider>
    );
};
