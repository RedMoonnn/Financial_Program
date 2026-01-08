import React, { useState, useEffect } from 'react';
import { Layout, Menu, ConfigProvider, theme, App as AntdApp } from 'antd';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  FileTextOutlined,
  MessageOutlined,
  UserOutlined,
  DatabaseOutlined,
  FolderOutlined,
  LogoutOutlined,
  TeamOutlined
} from '@ant-design/icons';
import Home from './pages/Home';
import Reports from './pages/Reports';
import Chat from './pages/Chat';
import UserCenter from './pages/UserCenter';
import AdminCollect from './pages/AdminCollect';
import AdminReports from './pages/AdminReports';
import AdminUsers from './pages/AdminUsers';
import Login from './pages/Login';
import Register from './pages/Register';
import Forgot from './pages/Forgot';
import EmailPreview from './pages/EmailPreview';
import './index.css';
import { isLogin, removeToken, isAdminSync, getUserInfo } from './auth';

const { Header, Content, Footer } = Layout;

const PrivateRoute = ({ element }: { element: JSX.Element }) => {
  return isLogin() ? element : <Navigate to="/login" replace />;
};

const AdminRoute = ({ element }: { element: JSX.Element }) => {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAdmin = async () => {
      if (!isLogin()) {
        setIsAdmin(false);
        setLoading(false);
        return;
      }

      let adminStatus = isAdminSync();
      if (adminStatus === false) {
        const userInfo = await getUserInfo();
        adminStatus = userInfo?.is_admin === true;
      }
      setIsAdmin(adminStatus);
      setLoading(false);
    };
    checkAdmin();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>加载中...</div>;
  }

  if (!isLogin()) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return element;
};

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const {
    token: { colorBgContainer, colorPrimary },
  } = theme.useToken();

  // 检查管理员权限
  useEffect(() => {
    const checkAdmin = async () => {
      if (isLogin()) {
        // 先尝试从缓存获取
        let adminStatus = isAdminSync();
        if (adminStatus === false) {
          // 如果缓存中没有，尝试从API获取
          const userInfo = await getUserInfo();
          adminStatus = userInfo?.is_admin === true;
        }
        setIsAdmin(adminStatus);
      }
    };
    checkAdmin();
  }, [location.pathname]);

  // 基础菜单项
  const baseMenuItems = [
    { key: 'home', icon: <HomeOutlined />, label: '首页', path: '/' },
    { key: 'reports', icon: <FileTextOutlined />, label: '历史报告', path: '/reports' },
    { key: 'chat', icon: <MessageOutlined />, label: '对话助手', path: '/chat' },
    { key: 'user', icon: <UserOutlined />, label: '用户中心', path: '/user' }
  ];

  // 管理员专属菜单项
  const adminMenuItems = [
    { key: 'admin-collect', icon: <DatabaseOutlined />, label: '数据采集', path: '/admin/collect' },
    { key: 'admin-reports', icon: <FolderOutlined />, label: '报告管理', path: '/admin/reports' },
    { key: 'admin-users', icon: <TeamOutlined />, label: '用户管理', path: '/admin/users' }
  ];

  // 合并菜单项
  const menuItems = isAdmin ? [...baseMenuItems, ...adminMenuItems] : baseMenuItems;

  const selectedKey = menuItems.find(item => location.pathname === item.path)?.key || 'home';

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      removeToken();
      navigate('/login');
    } else {
      const item = menuItems.find(i => i.key === key);
      if (item) navigate(item.path);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{
        background: colorBgContainer,
        padding: '0 24px',
        height: 64,
        display: 'flex',
        alignItems: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
      }}>
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* LOGO */}
          <div style={{
            fontWeight: 700,
            color: colorPrimary,
            fontSize: 24,
            flex: '0 0 auto',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            cursor: 'pointer'
          }} onClick={() => navigate('/')}>
            <span style={{ fontSize: 28 }}>⚡</span>
            智能金融数据采集分析平台
          </div>

          {/* 菜单 */}
          <Menu
            theme="light"
            mode="horizontal"
            selectedKeys={[selectedKey]}
            style={{
              flex: 1,
              minWidth: 400,
              justifyContent: 'flex-end',
              borderBottom: 'none',
              fontSize: 15,
              background: 'transparent',
              marginRight: 24
            }}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label
            }))}
            onClick={handleMenuClick}
          />

          {/* 用户/设置 */}
          {isLogin() && (
            <div
              style={{
                color: '#666',
                fontWeight: 500,
                fontSize: 14,
                cursor: 'pointer',
                flex: '0 0 auto',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '4px 12px',
                borderRadius: 20,
                background: '#f5f5f5',
                transition: 'all 0.3s'
              }}
              className="logout-btn"
              onClick={() => handleMenuClick({ key: 'logout' })}
            >
              <LogoutOutlined />
              退出登录
            </div>
          )}
        </div>
      </Header>
      <Content style={{
        width: '100%',
        maxWidth: 1400,
        margin: '24px auto',
        padding: '0 24px',
        minHeight: 'calc(100vh - 64px - 70px)',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<PrivateRoute element={<Home />} />} />
            <Route path="/reports" element={<PrivateRoute element={<Reports />} />} />
            <Route path="/chat" element={<PrivateRoute element={<Chat />} />} />
            <Route path="/user" element={<PrivateRoute element={<UserCenter />} />} />
            <Route path="/admin/collect" element={<AdminRoute element={<AdminCollect />} />} />
            <Route path="/admin/reports" element={<AdminRoute element={<AdminReports />} />} />
            <Route path="/admin/users" element={<AdminRoute element={<AdminUsers />} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center', background: 'transparent', color: '#888' }}>
        智能金融数据采集分析平台 ©2025 金融综设小组
      </Footer>
    </Layout>
  );
};

const App: React.FC = () => (
  <ConfigProvider
    theme={{
      token: {
        colorPrimary: '#1677ff',
        borderRadius: 8,
        wireframe: false,
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      },
      components: {
        Layout: {
          headerBg: '#ffffff',
          bodyBg: '#f0f2f5',
        },
        Menu: {
          itemColor: '#666',
          itemHoverColor: '#1677ff',
        },
        Button: {
          algorithm: true, // Enable automatic algorithm derivation
        }
      }
    }}
  >
    <AntdApp>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot" element={<Forgot />} />
          <Route path="/email-preview" element={<EmailPreview />} />
          <Route path="/*" element={<MainLayout />} />
        </Routes>
      </Router>
    </AntdApp>
  </ConfigProvider>
);

export default App;
