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
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/signup" element={
                        <PublicRoute>
                            <SignUpPage />
                        </PublicRoute>
                    } />
                    <Route path="/login" element={
                        <PublicRoute>
                            <LoginPage />
                        </PublicRoute>
                    } />
                    <Route
                        path="/chat/*" // 使用 /* 允许 ChatPage 内部嵌套路由
                        element={
                            <PrivateRoute>
                                <UserProfileProvider>
                                    <ChatPage />
                                </UserProfileProvider>
                            </PrivateRoute>
                        }
                    />
                    {/* 添加 Admin 主路由 */}
                    <Route path="/admin" element={
                        <PrivateRoute>
                            <UserProfileProvider>
                                <AdminLayout />
                            </UserProfileProvider>
                        </PrivateRoute>} >
                        <Route index element={<AdminDashboardPage />} />
                        <Route path="dashboard" element={<AdminDashboardPage />} />
                        <Route path="manage/:tableName" element={<AdminTableManagerPage />} /> {/* <--- 这个路由会匹配 */}
                    </Route>

                        <Route path="/" element={<Navigate to="/chat" />} />
                        {/* 可以添加一个404页面作为最后一个路由 */}
                        <Route path="*" element={<div>404 - Page Not Found</div>} />
                    {/* 其他 Admin 路由也可以使用 PrivateRoute */}
                    <Route path="/" element={<Navigate to="/chat" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;