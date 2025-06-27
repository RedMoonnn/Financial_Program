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
    { key: 'user', icon: <UserOutlined />, label: '用户中心', path: '/user' },
    { key: 'logout', icon: null, label: '退出登录', path: '/login' }
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
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#1677ff', padding: 0 }}>
        <div style={{ float: 'left', color: '#fff', fontWeight: 700, fontSize: 22, marginLeft: 32 }}>
          金融数据平台
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          style={{ background: '#1677ff', marginLeft: 200 }}
          items={menuItems
            .filter(item => item.key !== 'logout' || isLogin())
            .map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label
            }))}
          onClick={handleMenuClick}
        />
        {isLogin() && (
          <span style={{ float: 'right', color: '#fff', marginRight: 32, cursor: 'pointer' }} onClick={() => handleMenuClick({ key: 'logout' })}>
            退出登录
          </span>
        )}
      </Header>
      <Content style={{ margin: '24px 16px 0', background: '#fff', borderRadius: 8, minHeight: 600 }}>
        <Routes>
          <Route path="/" element={<PrivateRoute element={<Home />} />} />
          <Route path="/reports" element={<PrivateRoute element={<Reports />} />} />
          <Route path="/chat" element={<PrivateRoute element={<Chat />} />} />
          <Route path="/user" element={<PrivateRoute element={<UserCenter />} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Content>
      <Footer style={{ textAlign: 'center', background: '#f5f8fa' }}>
        金融数据平台 ©2024 Created by AI
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