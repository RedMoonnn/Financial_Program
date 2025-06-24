import React from 'react';
import { Table, Card, Row, Col } from 'antd';
import ReactECharts from 'echarts-for-react';

const columns = [
  { title: '代码', dataIndex: 'code', key: 'code', sorter: true },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '最新价', dataIndex: 'latest_price', key: 'latest_price', sorter: true },
  { title: '涨跌幅', dataIndex: 'change_percentage', key: 'change_percentage', sorter: true },
  { title: '主力净流入', dataIndex: 'main_flow_net_amount', key: 'main_flow_net_amount', sorter: true },
  { title: '主力净占比', dataIndex: 'main_flow_net_percentage', key: 'main_flow_net_percentage', sorter: true },
  { title: '超大单净流入', dataIndex: 'extra_large_order_flow_net_amount', key: 'extra_large_order_flow_net_amount', sorter: true },
  { title: '超大单净占比', dataIndex: 'extra_large_order_flow_net_percentage', key: 'extra_large_order_flow_net_percentage', sorter: true },
  { title: '大单净流入', dataIndex: 'large_order_flow_net_amount', key: 'large_order_flow_net_amount', sorter: true },
  { title: '大单净占比', dataIndex: 'large_order_flow_net_percentage', key: 'large_order_flow_net_percentage', sorter: true },
  { title: '中单净流入', dataIndex: 'medium_order_flow_net_amount', key: 'medium_order_flow_net_amount', sorter: true },
  { title: '中单净占比', dataIndex: 'medium_order_flow_net_percentage', key: 'medium_order_flow_net_percentage', sorter: true },
  { title: '小单净流入', dataIndex: 'small_order_flow_net_amount', key: 'small_order_flow_net_amount', sorter: true },
  { title: '小单净占比', dataIndex: 'small_order_flow_net_percentage', key: 'small_order_flow_net_percentage', sorter: true },
];

// 示例数据
const data: any[] = [];

const chartOption = {
  title: { text: '主力净流入/净流出', left: 'center', textStyle: { color: '#1677ff' } },
  tooltip: {},
  xAxis: { type: 'category', data: [] },
  yAxis: {},
  series: [
    {
      name: '主力净流入',
      type: 'bar',
      data: [],
      itemStyle: { color: '#1677ff' }
    },
    {
      name: '主力净流出',
      type: 'bar',
      data: [],
      itemStyle: { color: '#ff4d4f' }
    }
  ]
};

const Home: React.FC = () => {
  return (
    <div>
      <Row gutter={24}>
        <Col span={24}>
          <Card style={{ marginBottom: 24 }}>
            <ReactECharts option={chartOption} style={{ height: 320 }} />
          </Card>
        </Col>
      </Row>
      <Card>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="code"
          bordered
          scroll={{ x: 1600 }}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  );
};

export default Home; 