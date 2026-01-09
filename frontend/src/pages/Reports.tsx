import React from 'react';
import { List, Button, Popconfirm } from 'antd';
import { useReports } from '../hooks/useReports';
import { formatDateTime } from '../utils/dateUtils';

const Reports: React.FC = () => {
  const { reports, loading, deleteReport, downloadReport } = useReports({ autoLoad: true });

  const handleDelete = async (fileName: string) => {
    await deleteReport(fileName);
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 32 }}>
      <List
        header={<div style={{ fontWeight: 600, fontSize: 20 }}>历史报告列表</div>}
        bordered
        dataSource={reports}
        loading={loading}
        renderItem={item => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => downloadReport(item.url, item.file_name)} key="download">下载</Button>,
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
              {item.created_at && <span style={{ color: '#888', fontSize: 13, marginTop: 2 }}>生成时间：{formatDateTime(item.created_at)}</span>}
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

export default Reports;
