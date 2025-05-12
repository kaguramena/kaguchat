// frontend/src/admin/pages/AdminDashboardPage.js
import React from 'react';
import { Typography } from 'antd'; // 导入 Typography

const { Title, Paragraph } = Typography; // 解构 Title 和 Paragraph

const AdminDashboardPage = () => {
    return (
        <div>
            <Title level={2}>Admin Dashboard</Title>
            <Paragraph>
                Welcome to the KaguChat Admin Panel! This is the main dashboard.
            </Paragraph>
            <Paragraph>
                You can add various statistics, summaries, or quick links here.
            </Paragraph>
            {/* 你可以在这里添加一些统计信息或快捷链接 */}
        </div>
    );
};

export default AdminDashboardPage;
