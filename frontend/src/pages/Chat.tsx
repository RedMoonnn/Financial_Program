import React, { useState, useEffect } from 'react';
import { Card, Input, Button, List, message, Select, Cascader, Spin } from 'antd';
import axios from 'axios';
import { getToken, removeToken } from '../auth';

interface ChatProps {
  context?: any;
}

// 自动生成41种表单组合
const flowTypes = ['Stock_Flow', 'Sector_Flow'];
const marketTypes = [
  'All_Stocks', 'SH&SZ_A_Shares', 'SH_A_Shares', 'STAR_Market', 'SZ_A_Shares', 'ChiNext_Market', 'SH_B_Shares', 'SZ_B_Shares'
];
const detailTypes = ['Industry_Flow', 'Concept_Flow', 'Regional_Flow'];
const periods = ['today', '3d', '5d', '10d'];

interface TableOption {
  value: string;
  label: string;
}

const tableOptions: TableOption[] = [];
flowTypes.forEach(flow => {
  if (flow === 'Stock_Flow') {
    marketTypes.forEach(market => {
      periods.forEach(period => {
        tableOptions.push({
          value: `${flow}_${market}_${period}`,
          label: `${flow} - ${market} - ${period}`
        });
      });
    });
  } else {
    detailTypes.forEach(detail => {
      periods.forEach(period => {
        tableOptions.push({
          value: `${flow}_${detail}_${period}`,
          label: `${flow} - ${detail} - ${period}`
        });
      });
    });
  }
});

// 中文多级表单映射
const cascaderOptions = [
  {
    label: '个股资金流',
    value: 'Stock_Flow',
    children: [
      {
        label: '全部A股', value: 'All_Stocks',
        children: [
          { label: '今日', value: 'Today' },
          { label: '3日', value: '3_Day' },
          { label: '5日', value: '5_Day' },
          { label: '10日', value: '10_Day' },
        ]
      },
      { label: '沪深A股', value: 'SH&SZ_A_Shares', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '沪市A股', value: 'SH_A_Shares', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '科创板', value: 'STAR_Market', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '深市A股', value: 'SZ_A_Shares', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '创业板', value: 'ChiNext_Market', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '沪市B股', value: 'SH_B_Shares', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
      { label: '深市B股', value: 'SZ_B_Shares', children: [
        { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
      ] },
    ]
  },
  {
    label: '板块资金流',
    value: 'Sector_Flow',
    children: [
      {
        label: '行业板块', value: 'Industry_Flow',
        children: [
          { label: '今日', value: 'Today' },
          { label: '3日', value: '3_Day' },
          { label: '5日', value: '5_Day' },
          { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '概念板块', value: 'Concept_Flow',
        children: [
          { label: '今日', value: 'Today' },
          { label: '3日', value: '3_Day' },
          { label: '5日', value: '5_Day' },
          { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '区域板块', value: 'Regional_Flow',
        children: [
          { label: '今日', value: 'Today' },
          { label: '3日', value: '3_Day' },
          { label: '5日', value: '5_Day' },
          { label: '10日', value: '10_Day' },
        ]
      },
    ]
  }
];

const CHAT_HISTORY_KEY = 'financial_chat_history';

const Chat: React.FC<ChatProps> = ({ context }) => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<{ question: string; answer: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTableArr, setSelectedTableArr] = useState<string[] | undefined>();
  const [tableLoading, setTableLoading] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<any[]>(() => {
    const saved = localStorage.getItem(CHAT_HISTORY_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  // 聊天记录持久化
  useEffect(() => {
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory));
  }, [chatHistory]);

  // 清理历史对话，只保留有效的对话
  const cleanChatHistory = (history: any[]) => {
    if (!history || history.length === 0) return [];
    
    // 过滤掉无效对话
    const validHistory = history.filter(item => {
      const question = item.question?.trim() || '';
      return question.length > 3 && 
             !question.toLowerCase().includes('你好') &&
             !question.toLowerCase().includes('hello') &&
             !question.toLowerCase().includes('hi') &&
             !question.toLowerCase().includes('test');
    });
    
    // 只保留最近的10条对话
    return validHistory.slice(-10);
  };

  const handleSend = async () => {
    const tableName = getTableName(selectedTableArr);
    if (!input.trim() || !tableName) {
      message.warning('请先选择要分析的表单');
      return;
    }
    setChatLoading(true);
    try {
      // 传递清理后的历史对话
      const cleanedHistory = cleanChatHistory(chatHistory);
      
      const res = await axios.post('/api/ai/advice', {
        message: input,
        table_name: tableName,
        history: cleanedHistory  // 传递清理后的历史
      });
      let answer = res.data;
      if (!answer || (typeof answer === 'object' && Object.keys(answer).length === 0)) {
        answer = { advice: '未获取到分析结果', reasons: [], risks: [], detail: '' };
      }
      setChatHistory([...chatHistory, { question: input, answer }]);
      setInput('');
    } catch (e) {
      message.error('AI分析失败');
    }
    setChatLoading(false);
  };

  const parseAIAnswer = (answer: any) => {
    if (!answer) return '';
    if (typeof answer === 'string') {
      try {
        const obj = JSON.parse(answer);
        return obj;
      } catch {
        return answer;
      }
    }
    return answer;
  };

  // 拼接表名
  const getTableName = (arr: string[] | undefined) => {
    if (!arr || arr.length !== 3) return '';
    return arr.join('_');
  };

  // 清空聊天
  const handleClearChat = () => {
    setChatHistory([]);
    localStorage.removeItem(CHAT_HISTORY_KEY);
  };

  return (
    <div className="chat-page">
      {/* 表单选择区域 */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center' }}>
        <Cascader
          options={cascaderOptions}
          placeholder="请选择要分析的表单"
          value={selectedTableArr}
          onChange={setSelectedTableArr}
          expandTrigger="hover"
          style={{ width: 400 }}
        />
        <Button
          type="primary"
          style={{ marginLeft: 16 }}
          onClick={async () => {
            if (!selectedTableArr || selectedTableArr.length !== 3) {
              message.warning('请先选择要分析的表单');
              return;
            }
            if (!chatHistory || chatHistory.length === 0) {
              message.warning('请先与AI对话后再生成报告');
              return;
            }
            const hide = message.loading('报告生成中，请等待...', 0);
            try {
              const res = await axios.post('/api/report/generate', {
                table_name: getTableName(selectedTableArr),
                chat_history: chatHistory
              });
              hide();
              if (res.data && res.data.success) {
                message.success('报告生成成功！');
                window.location.href = '/reports';
              } else {
                message.error(res.data.error || '报告生成失败');
              }
            } catch (e) {
              hide();
              message.error('报告生成失败');
            }
          }}
        >生成报告</Button>
        <Button style={{ marginLeft: 16 }} danger onClick={handleClearChat}>清空聊天</Button>
      </div>
      {/* 聊天对话区 */}
      <div style={{ marginTop: 32 }}>
      <List
          dataSource={chatHistory}
          renderItem={item => (
          <List.Item>
              <div>
                <b>你：</b>{item.question}
                <br />
                <b>AI：</b>{
                  (item.answer?.advice &&
                    ["AI未能返回有效分析结果", "未获取到分析结果"].includes(item.answer.advice) &&
                    item.answer.reasons && item.answer.reasons.length > 0)
                    ? item.answer.reasons.join('\n')
                    : (item.answer?.advice || item.answer?.answer || '未获取到分析结果')
                }
            </div>
          </List.Item>
          )}
      />
        <Input.Search
        value={input}
        onChange={e => setInput(e.target.value)}
          onSearch={handleSend}
          enterButton="发送"
          loading={chatLoading}
          placeholder="请输入你的问题，如：主力流入最多的股票有哪些？"
        style={{ marginTop: 16 }}
          disabled={!selectedTableArr || selectedTableArr.length !== 3}
      />
      </div>
      {/* AI分析结果结构化展示 */}
      {aiResult && (
        <Card title="AI分析结果" style={{ marginBottom: 24 }}>
          {aiResult.advice && <div><b>结论：</b>{aiResult.advice}</div>}
          {aiResult.reasons && <div><b>理由：</b><ul>{aiResult.reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}</ul></div>}
          {aiResult.risks && aiResult.risks.length > 0 && <div><b>风险提示：</b><ul>{aiResult.risks.map((r: string, i: number) => <li key={i}>{r}</li>)}</ul></div>}
          {aiResult.detail && <div><b>详情：</b><pre style={{ whiteSpace: 'pre-wrap' }}>{aiResult.detail}</pre></div>}
          {aiResult.answer && <div><b>AI答复：</b><pre style={{ whiteSpace: 'pre-wrap' }}>{aiResult.answer}</pre></div>}
    </Card>
      )}
    </div>
  );
};

export default Chat; 