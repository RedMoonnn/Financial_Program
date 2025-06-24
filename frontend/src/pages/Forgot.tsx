import React, { useState } from 'react';
import { Card, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Forgot: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [codeLoading, setCodeLoading] = useState(false);
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  const sendCode = async () => {
    if (!email) return message.warning('请先输入邮箱');
    setCodeLoading(true);
    try {
      await axios.post('/api/auth/forgot', { email });
      message.success('验证码已发送');
    } catch {
      message.error('发送失败');
    }
    setCodeLoading(false);
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await axios.post('/api/auth/reset', values);
      message.success('密码重置成功');
      navigate('/login');
    } catch {
      message.error('重置失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 500 }}>
      <Card title="找回/重置密码" style={{ width: 360 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}> <Input onChange={e => setEmail(e.target.value)} /> </Form.Item>
          <Form.Item name="new_password" label="新密码" rules={[{ required: true, message: '请输入新密码' }]}> <Input.Password /> </Form.Item>
          <Form.Item name="code" label="验证码" rules={[{ required: true, message: '请输入验证码' }]}> <Input addonAfter={<Button size="small" loading={codeLoading} onClick={sendCode}>发送</Button>} /> </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ background: '#1677ff', borderColor: '#1677ff' }}>重置密码</Button>
          </Form.Item>
          <Form.Item>
            <Button type="link" onClick={() => navigate('/login')}>返回登录</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Forgot; 