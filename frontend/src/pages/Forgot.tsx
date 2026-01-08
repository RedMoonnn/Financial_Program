import React, { useState } from 'react';
import { Form, Input, Button, App, Typography } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import {
  MailOutlined,
  LockOutlined,
  SafetyCertificateOutlined,
  ArrowLeftOutlined,
  SendOutlined
} from '@ant-design/icons';
import axios from 'axios';
import './Forgot.css';

const { Title, Text } = Typography;

const Forgot: React.FC = () => {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [codeLoading, setCodeLoading] = useState(false);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const sendCode = async () => {
    try {
      // Validate email first
      await form.validateFields(['email']);
      const email = form.getFieldValue('email');

      setCodeLoading(true);
      await axios.post('/api/auth/forgot', { email });
      message.success('验证码已发送，请检查您的邮箱');
    } catch (error: any) {
      if (error?.errorFields) {
        // Validation error, do nothing
      } else {
        message.error('发送验证码失败，请重试');
      }
    } finally {
      setCodeLoading(false);
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await axios.post('/api/auth/reset', {
        email: values.email,
        new_password: values.new_password,
        code: values.code
      });
      message.success('密码重置成功！正在跳转登录页...');
      setTimeout(() => navigate('/login'), 1500);
    } catch {
      message.error('重置失败，请检查验证码是否正确');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-container">
      <div className="circle-1"></div>
      <div className="circle-2"></div>

      <div className="forgot-card">
        <div className="forgot-header">
          <Title level={2} className="forgot-title">找回密码</Title>
          <Text className="forgot-subtitle">请输入您的邮箱以获取验证码重置密码</Text>
        </div>

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
          requiredMark={false}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              className="custom-input"
              prefix={<MailOutlined style={{ color: '#1677ff' }} />}
              placeholder="请输入邮箱"
            />
          </Form.Item>

          <Form.Item
            name="new_password"
            rules={[
              { required: true, message: '请输入新密码' },
              { pattern: /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,20}$/, message: '密码需包含字母和数字，长度6-20位' }
            ]}
          >
            <Input.Password
              className="custom-input"
              prefix={<LockOutlined style={{ color: '#1677ff' }} />}
              placeholder="新密码 (包含字母和数字，6-20位)"
            />
          </Form.Item>

          <Form.Item
            name="confirm_new_password"
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
            <Input.Password
              className="custom-input"
              prefix={<LockOutlined style={{ color: '#1677ff' }} />}
              placeholder="确认新密码"
            />
          </Form.Item>

          <Form.Item>
            <div className="code-wrapper">
              <Form.Item
                name="code"
                noStyle
                rules={[{ required: true, message: '请输入验证码' }]}
              >
                <Input
                  className="custom-input"
                  prefix={<SafetyCertificateOutlined style={{ color: '#1677ff' }} />}
                  placeholder="验证码"
                  style={{ flex: 1 }}
                />
              </Form.Item>
              <Button
                className="send-code-btn"
                type="default"
                loading={codeLoading}
                onClick={sendCode}
                icon={!codeLoading && <SendOutlined />}
              >
                {codeLoading ? '发送中' : '获取验证码'}
              </Button>
            </div>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              className="submit-btn"
            >
              重置密码
            </Button>
          </Form.Item>

          <div className="back-link">
            <Link to="/login">
              <ArrowLeftOutlined style={{ marginRight: 4 }} />
              返回登录
            </Link>
          </div>
        </Form>
      </div>
    </div>
  );
};

export default Forgot;
