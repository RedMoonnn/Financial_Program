import React, { useState } from 'react';
import { Card, Button, Space, Typography, Divider, Tag, App } from 'antd';
import { PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const AdminCollect: React.FC = () => {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [collectAllLoading, setCollectAllLoading] = useState(false);

  // 单组合数据采集
  const handleSingleCollect = async () => {
    setLoading(true);
    try {
      // 默认采集：个股资金流 - 全部A股 - 今日 - 1页
      const response = await axios.post('/api/collect/collect_v2', {
        flow_choice: 1,
        market_choice: 1,
        day_choice: 1,
        pages: 1
      });

      if (response.data) {
        message.success(`采集成功！采集了 ${response.data.count || 0} 条数据`);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '采集失败';
      message.error(errorMsg);
    }
    setLoading(false);
  };

  // 全量数据采集
  const handleCollectAll = async () => {
    setCollectAllLoading(true);
    try {
      await axios.post('/api/collect/collect_all_v2');
      message.success('全量采集任务已启动，正在后台执行...');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '启动全量采集失败';
      message.error(errorMsg);
    }
    setCollectAllLoading(false);
  };

  return (
    <div style={{ width: '100%', maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <Card>
        <Title level={2}>数据采集管理</Title>
        <Text type="secondary">管理员可以手动触发数据采集任务</Text>

        <Divider />

        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Card
            title={
              <Space>
                <PlayCircleOutlined />
                <span>单组合数据采集</span>
              </Space>
            }
            extra={<Tag color="blue">快速采集</Tag>}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Text>
                采集指定组合的数据。默认采集：<strong>个股资金流 - 全部A股 - 今日</strong>
              </Text>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                提示：如需采集其他组合，请在首页使用&quot;手动更新&quot;功能
              </Text>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                loading={loading}
                onClick={handleSingleCollect}
                size="large"
              >
                开始单组合采集
              </Button>
            </Space>
          </Card>

          <Card
            title={
              <Space>
                <ReloadOutlined />
                <span>全量数据采集</span>
              </Space>
            }
            extra={<Tag color="orange">耗时较长</Tag>}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Text>
                采集所有组合的全部数据。此操作会采集所有市场类型和周期的数据，<strong>耗时较长</strong>。
              </Text>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                任务将在后台执行，不会阻塞当前操作
              </Text>
              <Button
                type="primary"
                danger
                icon={<ReloadOutlined />}
                loading={collectAllLoading}
                onClick={handleCollectAll}
                size="large"
              >
                启动全量采集
              </Button>
            </Space>
          </Card>
        </Space>
      </Card>
    </div>
  );
};

export default AdminCollect;
