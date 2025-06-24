import React from 'react';
import { Layout, Menu } from 'antd';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
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

const { Header, Content, Footer } = Layout;

const App: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ background: '#1677ff', padding: 0 }}>
          <div style={{ float: 'left', color: '#fff', fontWeight: 700, fontSize: 22, marginLeft: 32 }}>
            金融数据平台
          </div>
          <Menu
            theme="dark"
            mode="horizontal"
            defaultSelectedKeys={['home']}
            style={{ background: '#1677ff', marginLeft: 200 }}
          >
            <Menu.Item key="home" icon={<HomeOutlined />}>
              <Link to="/">首页</Link>
            </Menu.Item>
            <Menu.Item key="reports" icon={<FileTextOutlined />}>
              <Link to="/reports">历史报告</Link>
            </Menu.Item>
            <Menu.Item key="chat" icon={<MessageOutlined />}>
              <Link to="/chat">对话助手</Link>
            </Menu.Item>
            <Menu.Item key="user" icon={<UserOutlined />}>
              <Link to="/user">用户中心</Link>
            </Menu.Item>
          </Menu>
        </Header>
        <Content style={{ margin: '24px 16px 0', background: '#fff', borderRadius: 8, minHeight: 600 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/user" element={<UserCenter />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot" element={<Forgot />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center', background: '#f5f8fa' }}>
          金融数据平台 ©2024 Created by AI
        </Footer>
      </Layout>
    </Router>
  );
};

export default App; 