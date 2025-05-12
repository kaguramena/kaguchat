// frontend/src/admin/layouts/AdminLayout.js
import React, { useContext, useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation, NavLink } from 'react-router-dom';
import { Layout, Menu, Button, Spin, Alert, Typography, Avatar } from 'antd';
import {
    LogoutOutlined,
    DashboardOutlined,
    TableOutlined,
    UserOutlined
} from '@ant-design/icons';
import { AuthContext } from '../../contexts/AuthContext';
// 修正 UserProfileContext 的导入路径
import { UserProfileContext } from '../../contexts/UserProfileContext'; 
import { getAdminTables } from '../services/adminApi';

const { Header, Sider, Content } = Layout;
const { Title } = Typography; // Title 已从 antd 导入

const AdminLayout = () => {
    const { logout } = useContext(AuthContext);
    const { profile, isLoadingProfile } = useContext(UserProfileContext);
    const navigate = useNavigate();
    const location = useLocation();

    const [collapsed, setCollapsed] = useState(false);
    const [tables, setTables] = useState([]);
    const [isLoadingTables, setIsLoadingTables] = useState(true);
    const [tablesError, setTablesError] = useState(null);

    useEffect(() => {
        const fetchTables = async () => {
            setIsLoadingTables(true);
            try {
                const tablesData = await getAdminTables();
                setTables(tablesData || []);
                setTablesError(null);
            } catch (err) {
                console.error("Failed to fetch admin tables:", err);
                setTablesError(err.msg || "Could not load tables configuration");
                setTables([]);
            } finally {
                setIsLoadingTables(false);
            }
        };
        fetchTables();
    }, []);

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const generateMenuItems = () => {
        const items = [
            {
                key: '/admin',
                icon: <DashboardOutlined />,
                label: <NavLink to="/admin">Dashboard</NavLink>,
            },
        ];

        if (tables.length > 0) {
            items.push({
                key: 'tablesSubmenu',
                icon: <TableOutlined />,
                label: 'Manage Tables',
                children: tables.map(table => ({
                    key: `/admin/manage/${table.key}`,
                    label: <NavLink to={`/admin/manage/${table.key}`}>{table.displayName}</NavLink>,
                })),
            });
        }
        return items;
    };
    
    const currentSelectedKeys = [location.pathname];
    const defaultOpenKeys = tables.length > 0 && location.pathname.startsWith('/admin/manage/') ? ['tablesSubmenu'] : [];

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)} theme="dark">
                <div style={{ 
                    height: '32px', 
                    margin: '16px', 
                    background: 'rgba(255, 255, 255, 0.2)', 
                    textAlign: 'center', 
                    lineHeight: '32px', 
                    color: 'white', 
                    borderRadius: '4px',
                    overflow: 'hidden',
                    whiteSpace: 'nowrap',
                }}>
                    {collapsed ? 'KA' : 'KaguAdmin'}
                </div>
                {isLoadingTables && <Spin style={{ display: 'block', marginTop: '20px' }} />}
                {tablesError && <Alert message={tablesError} type="error" style={{ margin: '16px' }} />}
                {!isLoadingTables && !tablesError && (
                    <Menu
                        theme="dark"
                        mode="inline"
                        selectedKeys={currentSelectedKeys}
                        defaultOpenKeys={defaultOpenKeys}
                        items={generateMenuItems()}
                    />
                )}
            </Sider>
            <Layout className="site-layout">
                <Header style={{ padding: '0 24px', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    {/* Title 已导入并解构 */}
                    <Title level={3} style={{ margin: 0 }}>KaguChat Admin Panel</Title>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        {isLoadingProfile ? <Spin size="small" /> : profile ? (
                            <>
                                <Avatar src={profile.avatar_url} icon={!profile.avatar_url && <UserOutlined />} style={{ marginRight: 8 }} />
                                <span style={{ marginRight: '16px' }}>
                                    Welcome, {profile.nickname || profile.username}
                                </span>
                            </>
                        ) : (
                            <span style={{ marginRight: '16px' }}>Welcome, Admin</span>
                        )}
                        <Button type="default" icon={<LogoutOutlined />} onClick={handleLogout}>
                            Logout
                        </Button>
                    </div>
                </Header>
                <Content style={{ margin: '24px 16px', padding: 24, background: '#f0f2f5', minHeight: 280 }}>
                    <div style={{ padding: 24, background: '#fff', minHeight: '100%'}}>
                        <Outlet />
                    </div>
                </Content>
            </Layout>
        </Layout>
    );
};

export default AdminLayout;
