import React, { useEffect, useState } from 'react';
import { Tabs, Card, Button, Spin, Empty, Table, Tag, App } from 'antd';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';
import type { ColumnsType } from 'antd/es/table';
import { isAdminSync, getUserInfo } from '../auth';

// 后端参数映射 - 与后端完全对齐
const flowTypes = [
  { label: '个股资金流', value: 1 },
  { label: '板块资金流', value: 2 }
];

// 个股资金流市场类型映射
const marketTabs = [
  { label: '全部A股', value: 'All_Stocks' },
  { label: '沪深A股', value: 'SH&SZ_A_Shares' },
  { label: '沪市A股', value: 'SH_A_Shares' },
  { label: '科创板', value: 'STAR_Market' },
  { label: '深市A股', value: 'SZ_A_Shares' },
  { label: '创业板', value: 'ChiNext_Market' },
  { label: '沪市B股', value: 'SH_B_Shares' },
  { label: '深市B股', value: 'SZ_B_Shares' }
];

// 板块资金流类型映射
const detailTabs = [
  { label: '行业板块', value: 'Industry_Flow' },
  { label: '概念板块', value: 'Concept_Flow' },
  { label: '地域板块', value: 'Regional_Flow' }
];

// 个股资金流周期映射
const periodTabsStock = [
  { label: '今日', value: 'Today' },
  { label: '3日', value: '3_Day' },
  { label: '5日', value: '5_Day' },
  { label: '10日', value: '10_Day' }
];

// 板块资金流周期映射
const periodTabsSector = [
  { label: '今日', value: 'Today' },
  { label: '5日', value: '5_Day' },
  { label: '10日', value: '10_Day' }
];

interface TableRow {
  code: string;
  name: string;
  latest_price: number;
  change_percentage: number;
  main_flow_net_amount: number;
  main_flow_net_percentage: number;
  extra_large_order_flow_net_amount: number;
  extra_large_order_flow_net_percentage: number;
  large_order_flow_net_amount: number;
  large_order_flow_net_percentage: number;
  medium_order_flow_net_amount: number;
  medium_order_flow_net_percentage: number;
  small_order_flow_net_amount: number;
  small_order_flow_net_percentage: number;
  [key: string]: any;
}

const colorNumber = (val: number | string, type?: 'amount' | 'percent') => {
  if (val === undefined || val === null || val === '--') return <span>{val}</span>;
  let num = Number(val);
  let display = val;
  if (type === 'amount') {
    if (typeof val === 'number') {
      if (Math.abs(val) >= 1e8) display = (val / 1e8).toFixed(2) + '亿';
      else if (Math.abs(val) >= 1e4) display = (val / 1e4).toFixed(2) + '万';
      else display = val;
    } else if (typeof val === 'string' && !val.includes('亿') && !val.includes('万')) {
      const n = parseFloat(val);
      if (!isNaN(n)) {
        if (Math.abs(n) >= 1e8) display = (n / 1e8).toFixed(2) + '亿';
        else if (Math.abs(n) >= 1e4) display = (n / 1e4).toFixed(2) + '万';
        else display = val;
      }
    }
  }
  if (type === 'percent') {
    if (typeof val === 'number') display = val.toFixed(2) + '%';
    else if (typeof val === 'string' && !val.includes('%')) display = val + '%';
  }
  if (typeof display === 'string') {
    if (display.includes('亿')) num = parseFloat(display) * 1e8;
    else if (display.includes('万')) num = parseFloat(display) * 1e4;
    else if (display.includes('%')) num = parseFloat(display);
    else num = parseFloat(display);
  }
  let color = '#333';
  if (!isNaN(num)) {
    if (num > 0) color = '#e60000';
    else if (num < 0) color = '#009933';
  }
  return <span className="nowrap-cell" style={{ color }}>{num > 0 ? '+' : ''}{display}</span>;
};

const columns: ColumnsType<TableRow> = [
  { title: '代码', dataIndex: 'code', key: 'code', className: 'nowrap-cell', sorter: (a: TableRow, b: TableRow) => a.code.localeCompare(b.code) },
  { title: '名称', dataIndex: 'name', key: 'name', className: 'nowrap-cell', sorter: (a: TableRow, b: TableRow) => a.name.localeCompare(b.name) },
  {
    title: '最新价', dataIndex: 'latest_price', key: 'latest_price', className: 'nowrap-cell',
    sorter: (a: TableRow, b: TableRow) => a.latest_price - b.latest_price,
    render: (val: number): React.ReactNode => colorNumber(val !== undefined ? Number(val).toFixed(2) : '--', 'amount')
  },
  {
    title: '涨跌幅', dataIndex: 'change_percentage', key: 'change_percentage', className: 'nowrap-cell',
    sorter: (a: TableRow, b: TableRow) => a.change_percentage - b.change_percentage,
    render: (val: number): React.ReactNode => colorNumber(val, 'percent')
  },
  {
    title: '今日主力净流入',
    children: [
      {
        title: '净额',
        dataIndex: 'main_flow_net_amount',
        key: 'main_flow_net_amount',
        sorter: (a: TableRow, b: TableRow) => a.main_flow_net_amount - b.main_flow_net_amount,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'amount')
      },
      {
        title: '净占比',
        dataIndex: 'main_flow_net_percentage',
        key: 'main_flow_net_percentage',
        sorter: (a: TableRow, b: TableRow) => a.main_flow_net_percentage - b.main_flow_net_percentage,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'percent')
      }
    ]
  },
  {
    title: '今日超大单净流入',
    children: [
      {
        title: '净额',
        dataIndex: 'extra_large_order_flow_net_amount',
        key: 'extra_large_order_flow_net_amount',
        sorter: (a: TableRow, b: TableRow) => a.extra_large_order_flow_net_amount - b.extra_large_order_flow_net_amount,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'amount')
      },
      {
        title: '净占比',
        dataIndex: 'extra_large_order_flow_net_percentage',
        key: 'extra_large_order_flow_net_percentage',
        sorter: (a: TableRow, b: TableRow) => a.extra_large_order_flow_net_percentage - b.extra_large_order_flow_net_percentage,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'percent')
      }
    ]
  },
  {
    title: '今日大单净流入',
    children: [
      {
        title: '净额',
        dataIndex: 'large_order_flow_net_amount',
        key: 'large_order_flow_net_amount',
        sorter: (a: TableRow, b: TableRow) => a.large_order_flow_net_amount - b.large_order_flow_net_amount,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'amount')
      },
      {
        title: '净占比',
        dataIndex: 'large_order_flow_net_percentage',
        key: 'large_order_flow_net_percentage',
        sorter: (a: TableRow, b: TableRow) => a.large_order_flow_net_percentage - b.large_order_flow_net_percentage,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'percent')
      }
    ]
  },
  {
    title: '今日中单净流入',
    children: [
      {
        title: '净额',
        dataIndex: 'medium_order_flow_net_amount',
        key: 'medium_order_flow_net_amount',
        sorter: (a: TableRow, b: TableRow) => a.medium_order_flow_net_amount - b.medium_order_flow_net_amount,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'amount')
      },
      {
        title: '净占比',
        dataIndex: 'medium_order_flow_net_percentage',
        key: 'medium_order_flow_net_percentage',
        sorter: (a: TableRow, b: TableRow) => a.medium_order_flow_net_percentage - b.medium_order_flow_net_percentage,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'percent')
      }
    ]
  },
  {
    title: '今日小单净流入',
    children: [
      {
        title: '净额',
        dataIndex: 'small_order_flow_net_amount',
        key: 'small_order_flow_net_amount',
        sorter: (a: TableRow, b: TableRow) => a.small_order_flow_net_amount - b.small_order_flow_net_amount,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'amount')
      },
      {
        title: '净占比',
        dataIndex: 'small_order_flow_net_percentage',
        key: 'small_order_flow_net_percentage',
        sorter: (a: TableRow, b: TableRow) => a.small_order_flow_net_percentage - b.small_order_flow_net_percentage,
        className: 'nowrap-cell',
        render: (val: number): React.ReactNode => colorNumber(val, 'percent')
      }
    ]
  }
];

function getSortedChartOption(data: TableRow[]): any {
  const sorted = [...data].sort((a, b) => b.main_flow_net_amount - a.main_flow_net_amount);
  const names = sorted.map(d => d.name || d.code);
  const inflowData = sorted.map(d => d.main_flow_net_amount > 0 ? d.main_flow_net_amount : 0);
  const outflowData = sorted.map(d => d.main_flow_net_amount < 0 ? d.main_flow_net_amount : 0);
  return {
    title: {
      text: '主力净流入/净流出',
      left: 'center',
      textStyle: { color: '#1677ff' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        let str = params[0].name + '<br/>';
        params.forEach((item: any) => {
          str += `${item.marker}${item.seriesName}: ${item.value > 1e8 ? (item.value / 1e8).toFixed(2) + '亿' : item.value > 1e4 ? (item.value / 1e4).toFixed(2) + '万' : item.value}<br/>`;
        });
        return str;
      }
    },
    legend: {
      data: ['主力净流入', '主力净流出'],
      top: 30
    },
    grid: {
      left: 110, right: 60, bottom: 80, top: 60
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        rotate: 45,
        interval: 0,
        fontWeight: 'bold',
        fontSize: 16,
        color: '#222',
        margin: 24
      },
      axisLine: {
        lineStyle: { color: '#222', width: 2 }
      }
    },
    yAxis: {
      type: 'value',
      name: '金额',
      axisLabel: {
        fontWeight: 'bold',
        fontSize: 15,
        color: '#222',
        margin: 28,
        formatter: function (value: number) {
          if (value >= 1e8 || value <= -1e8) return (value / 1e8).toFixed(2) + '亿';
          if (value >= 1e4 || value <= -1e4) return (value / 1e4).toFixed(2) + '万';
          return value;
        }
      }
    },
    dataZoom: [
      { type: 'slider', show: true, xAxisIndex: 0, height: 20, bottom: 30, start: 0, end: 50 }
    ],
    series: [
      {
        name: '主力净流入',
        type: 'bar',
        stack: 'total',
        data: inflowData,
        itemStyle: { color: '#e60000' },
        barMaxWidth: 14,
        barGap: 0
      },
      {
        name: '主力净流出',
        type: 'bar',
        stack: 'total',
        data: outflowData,
        itemStyle: { color: '#009933' },
        barMaxWidth: 14,
        barGap: 0
      }
    ]
  };
}

const Home: React.FC = () => {
  const { message } = App.useApp();
  // 多级Tab状态
  const [flowChoice, setFlowChoice] = useState(1); // 1:个股 2:板块
  const [marketChoice, setMarketChoice] = useState(0); // 0~7
  const [detailChoice, setDetailChoice] = useState(0); // 0~2
  const [dayChoice, setDayChoice] = useState(0); // 0~3 or 0~2
  const [tableData, setTableData] = useState<any[]>([]);
  const [chartOption, setChartOption] = useState<any>(getSortedChartOption([]));
  const [crawlTime, setCrawlTime] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string>('');
  const [isAdmin, setIsAdmin] = useState(false);

  // 检查管理员权限
  useEffect(() => {
    const checkAdmin = async () => {
      let adminStatus = isAdminSync();
      if (adminStatus === false) {
        const userInfo = await getUserInfo();
        adminStatus = userInfo?.is_admin === true;
      }
      setIsAdmin(adminStatus);
    };
    checkAdmin();
  }, []);

  // 获取数据
  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      let params: any = {};
      if (flowChoice === 1) {
        // 个股资金流
        params = {
          flow_type: 'Stock_Flow',
          market_type: marketTabs[marketChoice].value,
          period: periodTabsStock[dayChoice].value
        };
      } else {
        // 板块资金流
        params = {
          flow_type: 'Sector_Flow',
          market_type: detailTabs[detailChoice].value,
          period: periodTabsSector[dayChoice].value
        };
      }

      console.log('请求参数:', params);
      const res = await axios.get('/api/flow', { params });

      if (res.data && res.data.data) {
        setTableData(res.data.data);
        if (res.data.data.length > 0) {
          setCrawlTime(res.data.data[0].crawl_time || '');
        } else {
          setCrawlTime('');
        }

        // 构建Echarts配置
        setChartOption(getSortedChartOption(res.data.data));
      } else {
        setTableData([]);
        setChartOption(getSortedChartOption([]));
        setCrawlTime('');
      }

      // 检查是否有错误信息
      if (res.data && res.data.error) {
        setError(res.data.error);
      }
    } catch (e: any) {
      console.error('获取数据失败:', e);
      const errorMsg = e.response?.data?.error || e.response?.data?.detail?.error || e.message || '获取数据失败';
      setError(errorMsg);
      setTableData([]);
      setChartOption(getSortedChartOption([]));
      setCrawlTime('');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, [flowChoice, marketChoice, detailChoice, dayChoice]);

  // 手动采集（仅管理员可用）
  const handleManualUpdate = async () => {
    if (!isAdmin) {
      message.warning('此功能仅管理员可用');
      return;
    }

    setUpdating(true);
    try {
      const body: any = { flow_choice: flowChoice, pages: 1 };
      if (flowChoice === 1) {
        body.market_choice = marketChoice + 1; // 后端从1开始
        body.day_choice = dayChoice + 1;
      } else {
        body.detail_choice = detailChoice + 1;
        body.day_choice = dayChoice + 1;
      }

      console.log('采集参数:', body);
      const res = await axios.post('/api/collect/collect_v2', body);
      // 直接用采集返回数据渲染
      if (res.data && res.data.data) {
        setTableData(res.data.data);
        if (res.data.data.length > 0) {
          setCrawlTime(res.data.data[0].crawl_time || '');
        } else {
          setCrawlTime('');
        }
        // 构建Echarts配置
        setChartOption(getSortedChartOption(res.data.data));
      }
      message.success('采集任务已完成');
    } catch (e: any) {
      console.error('采集失败:', e);
      const errorMsg = e.response?.data?.detail || '采集失败';
      message.error(errorMsg);
    }
    setUpdating(false);
  };

  // 多级Tab渲染
  return (
    <div style={{ width: '100%', paddingBottom: 32 }}>
      <Card variant="borderless" style={{ marginBottom: 24, borderRadius: 8 }}>
        <Tabs
          className="custom-tabs"
          activeKey={String(flowChoice)}
          onChange={k => {
            setFlowChoice(Number(k));
            setMarketChoice(0);
            setDetailChoice(0);
            setDayChoice(0);
          }}
          items={flowTypes.map(ft => ({
            key: String(ft.value),
            label: ft.label,
            children: (
              <Tabs
                className="custom-tabs"
                activeKey={String(flowChoice === 1 ? marketChoice : detailChoice)}
                onChange={k => {
                  if (flowChoice === 1) setMarketChoice(Number(k));
                  else setDetailChoice(Number(k));
                  setDayChoice(0);
                }}
                items={(flowChoice === 1 ? marketTabs : detailTabs).map((tab, index) => ({
                  key: String(index),
                  label: tab.label,
                  children: (
                    <Tabs
                      className="custom-tabs"
                      activeKey={String(dayChoice)}
                      onChange={k => setDayChoice(Number(k))}
                      items={(flowChoice === 1 ? periodTabsStock : periodTabsSector).map((pt, index) => ({
                        key: String(index),
                        label: pt.label,
                        children: (
                          <div style={{ marginTop: 16 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                {crawlTime && (
                                  <span style={{ color: '#888', fontSize: 14 }}>
                                    更新时间：{crawlTime}
                                  </span>
                                )}
                                {isAdmin && <Tag color="blue">管理员模式</Tag>}
                                {error && <span style={{ color: '#ff4d4f' }}>{error}</span>}
                              </div>
                              {isAdmin && (
                                <Button type="primary" loading={updating} onClick={handleManualUpdate} style={{ borderRadius: 6 }}>
                                  {updating ? '更新中' : '手动更新数据'}
                                </Button>
                              )}
                            </div>

                            <Card variant="borderless" style={{ marginBottom: 24, boxShadow: 'none', border: '1px solid #f0f0f0' }}>
                              {loading ? (
                                <div style={{ textAlign: 'center', padding: '60px' }}>
                                  <Spin size="large" />
                                  <div style={{ marginTop: 16, color: '#666' }}>数据加载中...</div>
                                </div>
                              ) : tableData.length > 0 ? (
                                <ReactECharts
                                  option={chartOption}
                                  style={{ height: 450, width: '100%' }}
                                  notMerge={true}
                                />
                              ) : (
                                <Empty description="暂无图表数据" style={{ padding: '60px' }} />
                              )}
                            </Card>

                            <Card variant="borderless" style={{ padding: 0, boxShadow: 'none' }}>
                              {tableData.length > 0 ? (
                                <Table
                                  className="custom-tight-table"
                                  columns={columns}
                                  dataSource={tableData}
                                  rowKey="code"
                                  variant="borderless"
                                  pagination={{ pageSize: 50, showSizeChanger: true }}
                                  scroll={{ x: 'max-content' }}
                                  size="middle"
                                />
                              ) : (
                                <Empty description="暂无表格数据" />
                              )}
                            </Card>
                          </div>
                        )
                      }))}
                    />
                  )
                }))}
              />
            )
          }))}
        />
      </Card>
    </div>
  );
};

export default Home;
