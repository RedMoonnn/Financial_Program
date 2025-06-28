import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { setToken, removeToken } from '../auth';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    document.title = '登录 - 金融数据平台';
  }, []);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // TODO: 替换为真实API
      const resp = await axios.post('/api/auth/login', values);
      // 假设后端返回 { token: 'xxx' }
      setToken(resp.data.access_token);
      message.success('登录成功');
      navigate('/');
    } catch {
      removeToken();
      message.error('登录失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 500 }}>
      <Card title="登录" style={{ width: 360 }}>
        <Form layout="vertical" onFinish={onFinish} onFinishFailed={({ errorFields }) => {
          if (errorFields && errorFields.length > 0) {
            message.error(errorFields[0].errors[0]);
          }
        }}>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '邮箱格式不正确' }
            ]}
          >
            <Input autoComplete="off" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password autoComplete="off" />
          </Form.Item>
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