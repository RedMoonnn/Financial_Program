import React, { useEffect, useState } from 'react';
import { Card, List, Button, Modal, message } from 'antd';
import axios from 'axios';
import { getToken, removeToken } from '../auth';

interface Report {
  id: number;
  type: string;
  file_url: string;
  file_name: string;
  created_at: string;
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = getToken();
    axios.get('/api/report/list', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setReports(res.data))
      .catch(() => {
        removeToken();
        message.error('请重新登录');
      });
  }, []);

  const handlePreview = async (report: Report) => {
    if (report.type !== 'markdown') {
      message.info('仅支持Markdown报告在线预览');
      return;
    }
    setLoading(true);
    try {
      const token = getToken();
      const resp = await axios.get(report.file_url, { headers: { Authorization: `Bearer ${token}` } });
      setPreview(resp.data);
    } catch {
      removeToken();
      message.error('预览失败，请重新登录');
    }
    setLoading(false);
  };

  return (
    <Card title="历史报告" bordered={false}>
      <List
        itemLayout="horizontal"
        dataSource={reports}
        renderItem={item => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => handlePreview(item)} key="preview">预览</Button>,
              <Button type="link" href={item.file_url} download={item.file_name} key="download">下载</Button>
            ]}
          >
            <List.Item.Meta
              title={item.file_name}
              description={`类型: ${item.type}  时间: ${item.created_at}`}
            />
          </List.Item>
        )}
      />
      <Modal
        open={!!preview}
        title="Markdown报告预览"
        onCancel={() => setPreview(null)}
        footer={null}
        width={800}
      >
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', background: '#f5f8fa', padding: 16 }}>{preview}</pre>
      </Modal>
    </Card>
  );
};

export default Reports; 