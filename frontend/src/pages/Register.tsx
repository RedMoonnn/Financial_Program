import React, { useState } from 'react';
import { Card, Input, Button, Form, App } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getErrorMessage } from '../utils/errorHandler';

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
      const response = await axios.post('/api/v1/auth/send_code', { email });
      // 后端返回的是 APIResponse 格式
      if (response.data?.success) {
        message.success(response.data.message || '验证码已发送');
      } else {
        throw new Error(response.data?.message || '发送失败');
      }
    } catch (err: any) {
      const errorMsg = getErrorMessage(err, '发送失败');
      if (errorMsg.includes('已注册')) {
        message.error('该邮箱已注册，请直接登录或找回密码');
      } else {
        message.error(errorMsg);
      }
    }
    setCodeLoading(false);
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/auth/register', {
        email: values.email,
        password: values.password,
        code: values.code
      });
      // 后端返回的是 APIResponse 格式
      if (response.data?.success) {
        message.success(response.data.message || '注册成功');
        navigate('/login');
      } else {
        throw new Error(response.data?.message || '注册失败');
      }
    } catch (err: any) {
      const errorMsg = getErrorMessage(err, '注册失败');
      if (errorMsg.includes('邮箱已注册') || errorMsg.includes('已注册')) {
        message.error('该邮箱已注册，请直接登录或找回密码');
      } else {
        message.error(errorMsg);
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
