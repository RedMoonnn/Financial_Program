import React, { useEffect, useState } from 'react';
import { Table, Card, Row, Col, Select, Spin } from 'antd';
import ReactECharts from 'echarts-for-react';
import { getToken, removeToken } from '../auth';
import axios from 'axios';
import Chat from './Chat';

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

const marketTypes = ['A股', '港股', '板块', '行业', '概念', '地域'];
const flowTypes = ['资金流向'];
const periods = [
  { label: '今日排行', value: 'today' },
  { label: '3日排行', value: '3d' },
  { label: '5日排行', value: '5d' },
  { label: '10日排行', value: '10d' }
];

const Home: React.FC = () => {
  const [dataReady, setDataReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [marketType, setMarketType] = useState('A股');
  const [flowType, setFlowType] = useState('资金流向');
  const [period, setPeriod] = useState('today');
  const [tableData, setTableData] = useState<any[]>([]);
  const [chartOption, setChartOption] = useState<any>(null);
  const [fetching, setFetching] = useState(false);

  useEffect(() => {
    const checkData = async () => {
      const resp = await axios.get('/api/data_ready');
      setDataReady(resp.data.data_ready);
      setLoading(false);
    };
    checkData();
    const timer = setInterval(checkData, 3000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!dataReady) return;
    setFetching(true);
    // 获取所有股票/行业/板块等数据（这里只做示例，实际应根据后端API返回的数据结构动态调整）
    axios.get('/api/flow', {
      params: {
        code: '', // 空代表全量或后端自动处理
        flow_type: flowType,
        market_type: marketType,
        period: period
      }
    }).then(res => {
      let data = res.data.data;
      if (!Array.isArray(data)) data = [data];
      setTableData(data);
      // 构建图表option
      setChartOption({
        title: { text: '主力净流入/净流出', left: 'center', textStyle: { color: '#1677ff' } },
        tooltip: {},
        xAxis: { type: 'category', data: data.map((d:any) => d.name) },
        yAxis: {},
        series: [
          {
            name: '主力净流入',
            type: 'bar',
            data: data.map((d:any) => d.main_flow_net_amount > 0 ? d.main_flow_net_amount : 0),
            itemStyle: { color: '#1677ff' }
          },
          {
            name: '主力净流出',
            type: 'bar',
            data: data.map((d:any) => d.main_flow_net_amount < 0 ? Math.abs(d.main_flow_net_amount) : 0),
            itemStyle: { color: '#ff4d4f' }
          }
        ]
      });
      setFetching(false);
    }).catch(() => setFetching(false));
  }, [dataReady, marketType, flowType, period]);

  if (loading || !dataReady) {
    return <div style={{textAlign:'center',marginTop:100,fontSize:20}}>正在收集数据，请稍后...</div>;
  }

  return (
    <div>
      <Row gutter={24} style={{ marginBottom: 16 }}>
        <Col>
          <Select value={marketType} onChange={setMarketType} options={marketTypes.map(t => ({ label: t, value: t }))} style={{ width: 120 }} />
        </Col>
        <Col>
          <Select value={flowType} onChange={setFlowType} options={flowTypes.map(t => ({ label: t, value: t }))} style={{ width: 120 }} />
        </Col>
        <Col>
          <Select value={period} onChange={setPeriod} options={periods} style={{ width: 120 }} />
        </Col>
      </Row>
      <Row gutter={24}>
        <Col span={24}>
          <Card style={{ marginBottom: 24 }}>
            {fetching ? <Spin /> : <ReactECharts option={chartOption} style={{ height: 320 }} />}
          </Card>
        </Col>
      </Row>
      <Card>
        <Table
          columns={columns}
          dataSource={tableData}
          rowKey="code"
          bordered
          scroll={{ x: 1600 }}
          pagination={{ pageSize: 20 }}
          loading={fetching}
        />
      </Card>
      <div style={{marginTop:32}}>
        <Chat context={{ marketType, flowType, period, tableData }} />
      </div>
      {/* Deepseek对话框后续集成 */}
    </div>
  );
};

export default Home; 