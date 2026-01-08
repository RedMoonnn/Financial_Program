import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { setToken, removeToken, getUserInfo } from '../auth';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    document.title = '登录 - 智能金融数据采集分析平台';
  }, []);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const resp = await axios.post('/api/auth/login', values);
      setToken(resp.data.access_token);
      // 登录成功后获取用户信息
      await getUserInfo();
      message.success('登录成功');
      navigate('/');
    } catch (error: any) {
      removeToken();
      const errorMsg = error.response?.data?.detail || '登录失败';
      message.error(errorMsg);
    }
    setLoading(false);
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%)'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
          <span style={{ fontSize: 36 }}>⚡</span>
          <span style={{ fontSize: 24, fontWeight: 700, color: '#1677ff' }}>智能金融数据平台</span>
        </div>
        <Card
          bordered={false}
          style={{
            width: 380,
            borderRadius: 12,
            boxShadow: '0 8px 24px rgba(0,0,0,0.05)'
          }}
        >
          <div style={{ marginBottom: 24, fontSize: 18, fontWeight: 600, color: '#333' }}>
            账号登录
          </div>
          <Form layout="vertical" onFinish={onFinish} size="large" onFinishFailed={({ errorFields }) => {
            if (errorFields && errorFields.length > 0) {
              message.error(errorFields[0].errors[0]);
            }
          }}>
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '邮箱格式不正确' }
              ]}
            >
              <Input placeholder="请输入邮箱" autoComplete="username" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password placeholder="请输入密码" autoComplete="current-password" />
            </Form.Item>
            <Form.Item style={{ marginBottom: 12 }}>
              <Button type="primary" htmlType="submit" loading={loading} block>
                立即登录
              </Button>
            </Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button type="link" onClick={() => navigate('/register')} style={{ padding: 0 }}>注册账号</Button>
              <Button type="link" onClick={() => navigate('/forgot')} style={{ padding: 0 }}>忘记密码</Button>
            </div>
          </Form>
        </Card>
      </div>
    </div>
  );
};

export default Login;
