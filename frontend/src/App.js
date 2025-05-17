// frontend/src/App.js
import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import { AuthProvider, AuthContext } from './contexts/AuthContext'; // 导入 AuthProvider
import ChatPage from './pages/ChatPage'; // 假设你创建了这个页面
import AdminLayout from './admin/layouts/AdminLayout'; // 导入 AdminLayout
import { UserProfileProvider } from './contexts/UserProfileContext'; // 导入 UserProfileProvider
import AdminDashboardPage from './admin/pages/AdminDashboardPage'; // 导入 AdminDashboardPage
import AdminTableManagerPage from './admin/pages/AdminTableManagerPage'; // 导入 AdminTableManagerPage
import SignUpPage from './pages/SignUpPage';

// 创建一个受保护的路由组件
const PrivateRoute = ({ children }) => {
    const { token, isLoadingAuth } = useContext(AuthContext);

    if (isLoadingAuth) {
        // 在初始token验证完成前，可以显示加载指示器
        return <div>Loading authentication status...</div>;
    }

    return token ? children : <Navigate to="/login" replace />; // replace 防止用户通过后退按钮回到受保护页面
};

// 公共路由，如果已登录则重定向到聊天页
const PublicRoute = ({ children }) => {
    const { token, isLoadingAuth } = useContext(AuthContext);

    if (isLoadingAuth) {
        return <div>Loading authentication status...</div>;
    }
    return token ? <Navigate to="/chat" replace /> : children;
};


function App() {
    return (
        <AuthProvider> {/* 1. AuthProvider 在最外层 */}
            <UserProfileProvider> {/* 2. UserProfileProvider 包裹所有可能需要 profile 的部分 */}
                <Router>
                    <Routes>
                        <Route path="/signup" element={
                            <PublicRoute> <SignUpPage /> </PublicRoute>
                        } />
                        <Route path="/login" element={
                            <PublicRoute> <LoginPage /> </PublicRoute>
                        } />

                        {/* 私有路由现在都共享同一个 UserProfileContext */}
                        <Route path="/chat/*" element={
                            <PrivateRoute> <ChatPage /> </PrivateRoute>
                        } />
                        <Route path="/admin" element={
                            <PrivateRoute> <AdminLayout /> </PrivateRoute>
                        }>
                            <Route index element={<AdminDashboardPage />} />
                            <Route path="dashboard" element={<AdminDashboardPage />} />
                            <Route path="manage/:tableName" element={<AdminTableManagerPage />} />
                        </Route>

                        <Route path="/" element={<Navigate to='/chat' />} />
                        <Route path="*" element={<div>404 - Page Not Found</div>} />
                    </Routes>
                </Router>
            </UserProfileProvider>
        </AuthProvider>
    );
}

export default App;