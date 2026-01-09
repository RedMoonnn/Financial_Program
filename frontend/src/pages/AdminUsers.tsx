import React from 'react';
import { Card, Table, Button, Popconfirm, Tag, Typography } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { useUsers } from '../hooks/useUsers';
import { formatDateTime } from '../utils/dateUtils';
import type { User } from '../types';

const { Title } = Typography;

const AdminUsers: React.FC = () => {
    const { users, loading, fetchUsers, deleteUser } = useUsers();

    const handleDelete = async (id: number) => {
        await deleteUser(id);
    };

    const columns = [
        { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
        { title: '邮箱', dataIndex: 'email', key: 'email' },
        { title: '用户名', dataIndex: 'username', key: 'username', render: (text: string) => text || '-' },
        {
            title: '角色',
            dataIndex: 'is_admin',
            key: 'is_admin',
            render: (isAdmin: boolean) => (
                isAdmin ? <Tag color="gold">管理员</Tag> : <Tag color="blue">普通用户</Tag>
            )
        },
        {
            title: '状态',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (active: boolean) => (
                active ? <Tag color="success">正常</Tag> : <Tag color="error">禁用</Tag>
            )
        },
        {
            title: '注册时间',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date: string) => formatDateTime(date)
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: User) => (
                <Popconfirm
                    title="确定要注销该用户吗？"
                    description="注销后该用户将无法登录，且数据可能被清理。"
                    onConfirm={() => handleDelete(record.id)}
                    okText="确定"
                    cancelText="取消"
                    disabled={record.is_admin}
                >
                    <Button danger icon={<DeleteOutlined />} size="small" disabled={record.is_admin}>
                        注销
                    </Button>
                </Popconfirm>
            )
        }
    ];

    return (
        <div style={{ width: '100%', maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
            <Card>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <Title level={2} style={{ margin: 0 }}>用户管理</Title>
                    <Button onClick={fetchUsers} loading={loading}>刷新</Button>
                </div>
                <Table
                    columns={columns}
                    dataSource={users}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 20 }}
                />
            </Card>
        </div>
    );
};

export default AdminUsers;
