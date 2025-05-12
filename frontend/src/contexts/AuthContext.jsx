import React, {useState, createContext, useEffect, useCallback} from "react";
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({children}) => {
    const [token, setToken] = useState(localStorage.getItem('authToken'));
    const [userId, setUserId] = useState(localStorage.getItem('userId'));
    const [isLoading, setIsLoading] = useState(true);
    const [csrfToken, setCsrfToken] = useState(localStorage.getItem('csrfToken'));
    // 设置默认 header， 让flask知道是谁
    // frontend/src/contexts/AuthContext.js
useEffect(() => {
    console.log('[AuthContext] Token effect triggered. Current token value:', token);
    console.log('[AuthContext] typeof axios:', typeof axios); // 检查 axios 类型
    console.log('[AuthContext] axios object:', axios); // 打印整个 axios 对象看它是什么

    if (axios) {
        console.log('[AuthContext] typeof axios.defaults:', typeof axios.defaults);
        console.log('[AuthContext] axios.defaults object:', axios.defaults);

        if (axios.defaults) {
            console.log('[AuthContext] typeof axios.defaults.headers:', typeof axios.defaults.headers);
            console.log('[AuthContext] axios.defaults.headers object:', axios.defaults.headers);

            // 现在才进行实际操作，并进行最终检查
            if (axios.defaults.headers) {
                if (token) {
                    console.log('[AuthContext] Setting Authorization header.');
                    // 尝试访问 common 前也检查一下
                    if (axios.defaults.headers.common) {
                       axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                    } else {
                       console.error('[AuthContext] CRITICAL: axios.defaults.headers.common is undefined! Initializing it.');
                       // 作为一个临时的补救/诊断措施，如果 common 不存在，尝试初始化它
                       // 这不应该是必需的，标准的 axios 会有这个
                       axios.defaults.headers.common = {};
                       axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                    }
                } else {
                    console.log('[AuthContext] Token is null, attempting to delete Authorization header.');
                    if (axios.defaults.headers.common) { // 确保 common 存在再删除属性
                       delete axios.defaults.headers.common['Authorization'];
                    } else {
                       console.warn('[AuthContext] axios.defaults.headers.common is undefined, cannot delete Authorization header from it.');
                    }
                }
            } else {
                console.error('[AuthContext] ERROR: axios.defaults.headers is undefined or null.');
            }
        } else {
            console.error('[AuthContext] ERROR: axios.defaults is undefined or null.');
        }
    } else {
        console.error('[AuthContext] ERROR: axios object is undefined or null.');
    }
}, [token]);

useEffect(() => {
    if (csrfToken) {
        console.log('[AuthContext] Setting X-CSRF-TOKEN header:', csrfToken);
        axios.defaults.headers.common['X-CSRF-TOKEN'] = csrfToken;
    } else {
        console.log('[AuthContext] CSRF Token is null, deleting X-CSRF-TOKEN header.');
        delete axios.defaults.headers.common['X-CSRF-TOKEN'];
    }
}, [csrfToken]); // 当 csrfToken 状态变化时执行

    const login = useCallback(async (username, password) => {
        console.log('[AuthContext] Attempting login with:', { username, password }); // <--- 新增日志
        try {
            const apiUrl = 'http://localhost:5001/api/auth/login'; // <--- 确认 API URL
            console.log('[AuthContext] Sending POST request to:', apiUrl); // <--- 新增日志

            const response = await axios.post(apiUrl, { // <--- 确保 axios 已正确导入和配置
                username,
                password
            });

            console.log('[AuthContext] Login API response:', response); // <--- 新增日志

            const { access_token, user_id, csrf_token } = response.data;
            localStorage.setItem('authToken', access_token);
            localStorage.setItem('userId', user_id);
            if(csrf_token){
                localStorage.setItem('csrfToken', csrf_token);
                console.log('[AuthContext] CSRF token stored:', csrf_token);
            } else {
                console.warn('[AuthContext] CSRF token not found in login response.');
                localStorage.removeItem('csrfToken'); // 如果不存在，确保清除旧的
            }
            setToken(access_token);
            setUserId(user_id);
            setCsrfToken(csrf_token || null); // <--- 更新 CSRF Token state
            console.log('[AuthContext] Login successful, token and userId stored.'); // <--- 新增日志
            return { success: true, userId: user_id };
        } catch (error) {
            // 这里非常重要，要打印详细的错误信息
            if (error.response) {
                // 请求已发出，服务器用状态码响应 (非 2xx)
                console.error('[AuthContext] Login API Error - Response status:', error.response.status);
                console.error('[AuthContext] Login API Error - Response data:', error.response.data);
                console.error('[AuthContext] Login API Error - Response headers:', error.response.headers);
            } else if (error.request) {
                // 请求已发出，但没有收到响应
                // `error.request` 在浏览器中是 XMLHttpRequest 实例，在 Node.js 中是 http.ClientRequest 实例
                console.error('[AuthContext] Login API Error - No response received. Request details:', error.request);
                console.error('[AuthContext] This could be a CORS issue, network error, or the backend server is down/unreachable.');
            } else {
                // 设置请求时发生了一些问题
                console.error('[AuthContext] Login API Error - Error setting up request:', error.message);
            }
            console.error('[AuthContext] Full error object:', error.config); // 打印请求配置

            localStorage.removeItem('authToken');
            localStorage.removeItem('userId');
            localStorage.removeItem('csrfToken');
            setToken(null);
            setUserId(null);
            setCsrfToken(null);
            return { success: false, error: error.response?.data?.msg || 'Login failed due to an unexpected error. Check console.' };
        }
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('csrfToken');
        setToken(null);
        setUserId(null);
        setCsrfToken(null);
    }, []);

    useEffect(() => {
        const validateToekn = async () =>{ 
            const storedToken = localStorage.getItem('authToken');
            const storedUserId = localStorage.getItem('userId');
            const storedCsrfToken = localStorage.getItem('csrfToken');

            if(storedToken && storedUserId){
                setToken(storedToken);
                setUserId(storedUserId);
                setCsrfToken(storedCsrfToken);
                try{
                    await axios.getItem('http://localhost:5001/api/auth/me');
                }catch (error){
                    console.log('Token validation failed on load, logging out.');
                    logout(); // Token 无效或过期
                }
            }
            setIsLoading(false);
        };
        validateToekn();
    }, [logout]);

    return (
        <AuthContext.Provider value = {{ token, userId, login, logout, isLoadingAuth: isLoading}}>
            {children}
        </AuthContext.Provider>
    )

};