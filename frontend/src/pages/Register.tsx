import React, { useState } from 'react';
import { Card, Input, Button, Form, App } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register: React.FC = () => {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [codeLoading, setCodeLoading] = useState(false);
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  const sendCode = async () => {
    if (!email) return message.warning('请先输入邮箱');
    setCodeLoading(true);
    try {
      await axios.post('/api/auth/send_code', { email });
      message.success('验证码已发送');
    } catch (err: any) {
      if (err?.response?.data?.detail?.includes('已注册')) {
        message.error('该邮箱已注册，请直接登录或找回密码');
      } else {
        message.error('发送失败');
      }
    }
    setCodeLoading(false);
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await axios.post('/api/auth/register', {
        email: values.email,
        password: values.password,
        code: values.code
      });
      message.success('注册成功');
      navigate('/login');
    } catch (err: any) {
      if (err?.response?.data?.detail?.includes('邮箱已注册')) {
        message.error('该邮箱已注册，请直接登录或找回密码');
      } else {
        message.error('注册失败');
      }
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 500 }}>
      <Card title="注册账号" style={{ width: 360 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}>
            <Input onChange={e => setEmail(e.target.value)} />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item
            name="confirm"
            label="确认密码"
            dependencies={["password"]}
            hasFeedback
            rules={[
              { required: true, message: '请再次输入密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致!'));
                },
              }),
            ]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item name="code" label="验证码" rules={[{ required: true, message: '请输入验证码' }]}>
            <Input addonAfter={<Button size="small" loading={codeLoading} onClick={sendCode}>发送</Button>} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ background: '#1677ff', borderColor: '#1677ff' }}>注册</Button>
          </Form.Item>
          <Form.Item>
            <Button type="link" onClick={() => navigate('/login')}>已有账号？去登录</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Register;
