import React from 'react';
import { Card, Table, Button, Popconfirm, Space, Typography, Divider, Tag } from 'antd';
import { DeleteOutlined, FileTextOutlined, DownloadOutlined, UserOutlined } from '@ant-design/icons';
import { useReports } from '../hooks/useReports';
import type { ReportFile } from '../types';
import { formatDateTimeLocal } from '../utils/dateUtils';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

const AdminReports: React.FC = () => {
  const { reports, loading, fetchReports, deleteReport, downloadReport } = useReports({ autoLoad: true });

  const handleDelete = async (fileName: string) => {
    await deleteReport(fileName);
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
      render: (text: string) => formatDateTimeLocal(text),
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
            onClick={() => downloadReport(record.url, record.file_name)}
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
