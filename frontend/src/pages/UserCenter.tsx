import React, { useState, useEffect } from 'react';
import { Card, Descriptions, Tag, Typography, Space } from 'antd';
import { UserOutlined, MailOutlined, CrownOutlined } from '@ant-design/icons';
import { getUserInfo, UserInfo } from '../auth';

const { Title } = Typography;

const UserCenter: React.FC = () => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserInfo = async () => {
      setLoading(true);
      const info = await getUserInfo();
      setUserInfo(info);
      setLoading(false);
    };
    fetchUserInfo();
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        加载中...
      </div>
    );
  }

  if (!userInfo) {
    return (
      <div style={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, color: '#888' }}>
        无法获取用户信息
      </div>
    );
  }

  return (
    <div style={{ width: '100%', maxWidth: 800, margin: '0 auto', padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={2}>
            <UserOutlined /> 用户中心
          </Title>

          <Descriptions bordered column={1}>
            <Descriptions.Item label="用户ID">
              {userInfo.id}
            </Descriptions.Item>
            <Descriptions.Item label="邮箱">
              <Space>
                <MailOutlined />
                {userInfo.email}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="用户名">
              {userInfo.username || '未设置'}
            </Descriptions.Item>
            <Descriptions.Item label="账户状态">
              {userInfo.is_active ? (
                <Tag color="green">已激活</Tag>
              ) : (
                <Tag color="red">未激活</Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="用户角色">
              {userInfo.is_admin ? (
                <Tag color="orange" icon={<CrownOutlined />}>
                  管理员
                </Tag>
              ) : (
                <Tag>普通用户</Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="注册时间">
              {userInfo.created_at ? new Date(userInfo.created_at).toLocaleString('zh-CN') : '未知'}
            </Descriptions.Item>
          </Descriptions>

          {userInfo.is_admin && (
            <Card type="inner" style={{ background: '#fff7e6', borderColor: '#ffd591' }}>
              <Space direction="vertical">
                <Title level={4} style={{ margin: 0 }}>
                  <CrownOutlined /> 管理员权限
                </Title>
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  <li>可以访问数据采集管理页面</li>
                  <li>可以访问报告管理页面</li>
                  <li>可以在首页使用“手动更新”功能</li>
                  <li>可以查看和删除所有用户的报告</li>
                </ul>
              </Space>
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default UserCenter;
