import React from 'react';
import { Card, Descriptions, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { getToken, removeToken } from '../auth';
import { useEffect, useState } from 'react';
import axios from 'axios';

const UserCenter: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<{ email: string; created_at: string } | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      navigate('/login');
      return;
    }
    axios.get('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setUser(res.data))
      .catch(() => {
        removeToken();
        navigate('/login');
      });
  }, [navigate]);

  if (!user) return null;

  return (
    <Card title="用户中心" bordered={false}>
      <Descriptions column={1} bordered>
        <Descriptions.Item label="邮箱">{user.email}</Descriptions.Item>
        <Descriptions.Item label="注册时间">{user.created_at}</Descriptions.Item>
      </Descriptions>
      <Button type="link" onClick={() => navigate('/forgot')} style={{ marginTop: 16 }}>
        重置密码
      </Button>
    </Card>
  );
};

export default UserCenter; 