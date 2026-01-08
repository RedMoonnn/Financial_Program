import React, { useState } from 'react';
import { Card, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Forgot: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [codeLoading, setCodeLoading] = useState(false);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const sendCode = async () => {
    const email = form.getFieldValue('email');
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
      await axios.post('/api/auth/reset', {
        email: values.email,
        new_password: values.new_password,
        code: values.code
      });
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
        <Form form={form} layout="vertical" onFinish={onFinish} autoComplete="off">
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }]}> <Input /> </Form.Item>
          <Form.Item name="new_password" label="新密码" rules={[
            { required: true, message: '请输入新密码' },
            { pattern: /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,20}$/, message: '密码需包含字母和数字，长度6-20位' }
          ]}> <Input.Password autoComplete="new-password" /> </Form.Item>
          <Form.Item
            name="confirm_new_password"
            label="确认新密码"
            dependencies={["new_password"]}
            hasFeedback
            rules={[
              { required: true, message: '请再次输入新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的新密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password autoComplete="new-password" />
          </Form.Item>
          <Form.Item name="code" label="验证码" rules={[{ required: true, message: '请输入验证码' }]}>
            <Input
              autoComplete="off"
              addonAfter={
                <Button size="small" loading={codeLoading} onClick={sendCode}>发送</Button>
              }
            />
          </Form.Item>
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
