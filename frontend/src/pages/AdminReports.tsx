import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Popconfirm, Space, Typography, Divider, App, Tag } from 'antd';
import { DeleteOutlined, FileTextOutlined, DownloadOutlined, UserOutlined } from '@ant-design/icons';
import axios from 'axios';
import { getToken } from '../auth';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface ReportFile {
  file_name: string;
  url: string;
  created_at?: string;
  user_id?: number;
  user_email?: string;
  username?: string;
}

const AdminReports: React.FC = () => {
  const { message } = App.useApp();
  const [reports, setReports] = useState<ReportFile[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取所有报告文件
  const fetchReports = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const response = await axios.get('/api/report/minio_list', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.data) {
        // 按创建时间倒序排序
        const sorted = [...response.data].sort((a, b) => {
          if (a.created_at && b.created_at) {
            return b.created_at.localeCompare(a.created_at);
          } else if (a.created_at) {
            return -1;
          } else if (b.created_at) {
            return 1;
          } else {
            return 0;
          }
        });
        setReports(sorted);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '获取报告列表失败';
      message.error(errorMsg);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // 删除报告
  const handleDelete = async (fileName: string) => {
    try {
      const token = getToken();
      const res = await axios.delete('/api/report/delete', {
        params: { file_name: fileName },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.data && res.data.success) {
        message.success(`已删除 ${fileName}`);
        fetchReports(); // 刷新列表
      } else {
        message.error(res.data?.msg || '删除失败');
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '删除失败';
      message.error(errorMsg);
    }
  };

  // 下载报告
  const handleDownload = (url: string) => {
    window.open(url, '_blank');
  };

  const columns: ColumnsType<ReportFile> = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text: string) => (
        <Space>
          <FileTextOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '所有者',
      key: 'owner',
      width: 200,
      render: (_, record) => {
        if (record.user_email) {
          return (
            <Space>
              <UserOutlined />
              <span>{record.username || record.user_email}</span>
            </Space>
          );
        }
        return <Tag>未知</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => text ? new Date(text).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record.url)}
          >
            下载
          </Button>
          <Popconfirm
            title="确定要删除这个报告吗？"
            onConfirm={() => handleDelete(record.file_name)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ width: '100%', maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Title level={2}>报告管理</Title>
            <Text type="secondary">查看和管理所有用户的报告文件</Text>
          </div>

          <Divider />

          <Space style={{ marginBottom: 16 }}>
            <Button onClick={fetchReports} loading={loading}>
              刷新列表
            </Button>
            <Text type="secondary">
              共 {reports.length} 个报告文件
            </Text>
          </Space>

          <Table
            columns={columns}
            dataSource={reports}
            rowKey="file_name"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个报告`,
            }}
          />
        </Space>
      </Card>
    </div>
  );
};

export default AdminReports;
