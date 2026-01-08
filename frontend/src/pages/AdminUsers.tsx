import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Popconfirm, Tag, App, Typography } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { Title } = Typography;

interface User {
    id: number;
    email: string;
    username: string | null;
    is_admin: boolean;
    is_active: boolean;
    created_at: string | null;
}

const AdminUsers: React.FC = () => {
    const { message } = App.useApp();
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<User[]>([]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const resp = await axios.get('/api/auth/users');
            setData(resp.data);
        } catch (error: any) {
            if (error.response?.status !== 401) {
                message.error('获取用户列表失败');
            }
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleDelete = async (id: number) => {
        try {
            await axios.delete(`/api/auth/users/${id}`);
            message.success('用户已注销');
            fetchData(); // reload
        } catch (error: any) {
            message.error(error.response?.data?.detail || '注销失败');
        }
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
            render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
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
                    <Button onClick={fetchData} loading={loading}>刷新</Button>
                </div>
                <Table
                    columns={columns}
                    dataSource={data}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 20 }}
                />
            </Card>
        </div>
    );
};

export default AdminUsers;
