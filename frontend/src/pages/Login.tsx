import React, { useState } from 'react';
import { Card, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // TODO: 替换为真实API
      await axios.post('/api/auth/login', values);
      message.success('登录成功');
      navigate('/');
    } catch {
      message.error('登录失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 500 }}>
      <Card title="登录" style={{ width: 360 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}> <Input /> </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}> <Input.Password /> </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ background: '#1677ff', borderColor: '#1677ff' }}>登录</Button>
          </Form.Item>
          <Form.Item>
            <Button type="link" onClick={() => navigate('/register')}>注册账号</Button>
            <Button type="link" onClick={() => navigate('/forgot')}>忘记密码</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 