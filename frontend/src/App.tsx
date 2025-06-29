import React from 'react';
import { Layout, Menu } from 'antd';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  FileTextOutlined,
  MessageOutlined,
  UserOutlined
} from '@ant-design/icons';
import Home from './pages/Home';
import Reports from './pages/Reports';
import Chat from './pages/Chat';
import UserCenter from './pages/UserCenter';
import Login from './pages/Login';
import Register from './pages/Register';
import Forgot from './pages/Forgot';
import './index.css';
import { isLogin, removeToken } from './auth';

const { Header, Content, Footer } = Layout;

const PrivateRoute = ({ element }: { element: JSX.Element }) => {
  return isLogin() ? element : <Navigate to="/login" replace />;
};

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const menuItems = [
    { key: 'home', icon: <HomeOutlined />, label: '首页', path: '/' },
    { key: 'reports', icon: <FileTextOutlined />, label: '历史报告', path: '/reports' },
    { key: 'chat', icon: <MessageOutlined />, label: '对话助手', path: '/chat' },
    { key: 'user', icon: <UserOutlined />, label: '用户中心', path: '/user' }
  ];
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
    <Layout style={{ minHeight: '100vh', background: '#f5f8fa' }}>
      <Header style={{ background: '#1677ff', padding: 0, height: 56, display: 'flex', alignItems: 'center' }}>
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* LOGO */}
          <div style={{ fontWeight: 700, color: '#fff', fontSize: 22, flex: '0 0 auto' }}>
            智能金融数据采集分析平台
          </div>
          {/* 菜单 */}
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[selectedKey]}
            style={{ background: 'transparent', flex: 1, minWidth: 400, justifyContent: 'center', borderBottom: 'none', fontSize: 16 }}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label
            }))}
            onClick={handleMenuClick}
          />
          {/* 用户/设置 */}
          {isLogin() && (
            <div style={{ color: '#fff', fontWeight: 500, fontSize: 16, marginLeft: 32, cursor: 'pointer', flex: '0 0 auto' }} onClick={() => handleMenuClick({ key: 'logout' })}>
              退出登录
            </div>
          )}
        </div>
      </Header>
      <Content style={{ width: '100%', maxWidth: 1400, margin: '32px auto 0 auto', padding: '0 32px', minHeight: 600, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Routes>
          <Route path="/" element={<PrivateRoute element={<Home />} />} />
          <Route path="/reports" element={<PrivateRoute element={<Reports />} />} />
          <Route path="/chat" element={<PrivateRoute element={<Chat />} />} />
          <Route path="/user" element={<PrivateRoute element={<UserCenter />} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Content>
      <Footer style={{ textAlign: 'center', background: '#f5f8fa', width: '100%', maxWidth: 1400, margin: '0 auto', padding: 0 }}>
        智能金融数据采集分析平台 ©2025 金融综设小组 
      </Footer>
    </Layout>
  );
};

const App: React.FC = () => (
  <Router>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot" element={<Forgot />} />
      <Route path="/*" element={<MainLayout />} />
    </Routes>
  </Router>
);

export default App; 