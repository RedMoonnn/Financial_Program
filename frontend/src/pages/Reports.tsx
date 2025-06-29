import React, { useEffect, useState } from 'react';
import { List, Button, message, Tag, Popconfirm } from 'antd';
import axios from 'axios';

interface Report {
  file_name: string;
  url: string;
  created_at?: string;
}

// 生成MinIO控制台API下载链接
const getMinioDownloadUrl = (fileName: string) =>
  `http://192.168.211.99:9001/api/v1/buckets/data-financial-agent/objects/download?prefix=${encodeURIComponent(fileName)}&version_id=null`;

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchReports = () => {
    axios.get('/api/report/minio_list')
      .then(res => {
        // 严格按created_at时间戳倒序排序，无created_at的排在最后
        const sorted = [...res.data].sort((a, b) => {
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
      })
      .catch(() => {
        message.error('获取报告列表失败');
      });
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (fileName: string) => {
    setLoading(true);
    try {
      const res = await axios.delete('/api/report/delete', { params: { file_name: fileName } });
      if (res.data && res.data.success) {
        message.success('删除成功');
        fetchReports();
      } else {
        message.error(res.data.msg || '删除失败');
      }
    } catch {
      message.error('删除失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 32 }}>
      <List
        header={<div style={{ fontWeight: 600, fontSize: 20 }}>历史报告列表（MinIO）</div>}
        bordered
        dataSource={reports}
        loading={loading}
        renderItem={item => (
          <List.Item
            actions={[
              <Button type="link" href={getMinioDownloadUrl(item.file_name)} download={item.file_name} key="download">下载</Button>,
              <Popconfirm
                title="确定要删除该报告吗？"
                onConfirm={() => handleDelete(item.file_name)}
                okText="删除"
                cancelText="取消"
                key="delete"
              >
                <Button type="link" danger>删除</Button>
              </Popconfirm>
            ]}
          >
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontWeight: 500 }}>{item.file_name}</span>
              {item.created_at && <span style={{ color: '#888', fontSize: 13, marginTop: 2 }}>生成时间：{item.created_at}</span>}
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

export default Reports; 