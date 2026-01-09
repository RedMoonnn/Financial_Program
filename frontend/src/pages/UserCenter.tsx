import React, { useState, useEffect } from 'react';
import { Card, Descriptions, Tag, Typography, Space, Input, Button } from 'antd';
import { UserOutlined, MailOutlined, CrownOutlined, EditOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import axios from 'axios';
import { getUserInfo } from '../auth';
import type { User } from '../types';
import { callAPIWithErrorHandling } from '../utils/apiUtils';

const { Title } = Typography;

const UserCenter: React.FC = () => {
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingUsername, setEditingUsername] = useState(false);
  const [usernameValue, setUsernameValue] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchUserInfo = async () => {
      setLoading(true);
      const info = await getUserInfo();
      setUserInfo(info);
      if (info) {
        setUsernameValue(info.username || '');
      }
      setLoading(false);
    };
    fetchUserInfo();
  }, []);

  const handleEditUsername = () => {
    setEditingUsername(true);
    setUsernameValue(userInfo?.username || '');
  };

  const handleCancelEdit = () => {
    setEditingUsername(false);
    setUsernameValue(userInfo?.username || '');
  };

  const handleSaveUsername = async () => {
    const trimmedUsername = usernameValue.trim();
    const newUsername = trimmedUsername || null;

    // 如果用户名没有变化，直接退出编辑模式
    if (newUsername === (userInfo?.username || null)) {
      setEditingUsername(false);
      return;
    }

    setSaving(true);
    try {
      const updatedUserData = await callAPIWithErrorHandling<User>(
        async () => {
          const response = await axios.put('/api/v1/auth/me/username', {
            username: newUsername,
          });
          return response; // 返回完整的 axios 响应对象 { data: APIResponse<User> }
        },
        {
          successMsg: '用户名更新成功',
          showSuccess: true,
          showError: true,
        }
      );

      // callAPIWithErrorHandling 已经返回了 data 字段（User 类型）
      if (updatedUserData) {
        setUserInfo(updatedUserData);
        // 更新缓存
        localStorage.setItem('userInfo', JSON.stringify(updatedUserData));
        setEditingUsername(false);
      }
    } catch (error: any) {
      console.error('更新用户名失败:', error);
      // 错误信息已经由 callAPIWithErrorHandling 显示，这里不需要额外处理
    } finally {
      setSaving(false);
    }
  };

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
              {editingUsername ? (
                <Space>
                  <Input
                    value={usernameValue}
                    onChange={(e) => setUsernameValue(e.target.value)}
                    placeholder="请输入用户名"
                    maxLength={64}
                    style={{ width: 200 }}
                    onPressEnter={handleSaveUsername}
                  />
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={handleSaveUsername}
                    loading={saving}
                    size="small"
                  >
                    保存
                  </Button>
                  <Button
                    icon={<CloseOutlined />}
                    onClick={handleCancelEdit}
                    disabled={saving}
                    size="small"
                  >
                    取消
                  </Button>
                </Space>
              ) : (
                <Space>
                  <span>{userInfo.username || '未设置'}</span>
                  <Button
                    type="link"
                    icon={<EditOutlined />}
                    onClick={handleEditUsername}
                    size="small"
                  >
                    编辑
                  </Button>
                </Space>
              )}
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
