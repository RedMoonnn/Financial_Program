import React from 'react';
import { Card, Descriptions, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

const UserCenter: React.FC = () => {
  const navigate = useNavigate();
  // TODO: 替换为真实用户信息
  const user = { email: 'user@example.com', created_at: '2024-06-01' };

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