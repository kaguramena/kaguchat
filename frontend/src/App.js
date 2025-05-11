// frontend/src/App.js
import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import { AuthProvider, AuthContext } from './contexts/AuthContext'; // 导入 AuthProvider
import ChatPage from './pages/ChatPage'; // 假设你创建了这个页面

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
                    <Route path="/login" element={
                        <PublicRoute>
                            <LoginPage />
                        </PublicRoute>
                    } />
                    <Route
                        path="/chat/*" // 使用 /* 允许 ChatPage 内部嵌套路由
                        element={
                            <PrivateRoute>
                                <ChatPage />
                            </PrivateRoute>
                        }
                    />
                    {/* 其他 Admin 路由也可以使用 PrivateRoute */}
                    <Route path="/" element={<Navigate to="/chat" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;