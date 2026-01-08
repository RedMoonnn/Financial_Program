import React, { useState, useEffect, useRef } from 'react';
import { Card, Input, Button, message, Cascader, Spin, Avatar } from 'antd';
import { UserOutlined, RobotOutlined, ClearOutlined, FileTextOutlined } from '@ant-design/icons';
import axios from 'axios';
import { getToken } from '../auth';

interface ChatProps {
  context?: any;
}

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
      {
        label: '沪深A股', value: 'SH&SZ_A_Shares', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '沪市A股', value: 'SH_A_Shares', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '科创板', value: 'STAR_Market', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '深市A股', value: 'SZ_A_Shares', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '创业板', value: 'ChiNext_Market', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '沪市B股', value: 'SH_B_Shares', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
      {
        label: '深市B股', value: 'SZ_B_Shares', children: [
          { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
        ]
      },
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

const Chat: React.FC<ChatProps> = () => {
  const [input, setInput] = useState('');
  const [selectedTableArr, setSelectedTableArr] = useState<string[] | undefined>();
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<any[]>(() => {
    const saved = localStorage.getItem(CHAT_HISTORY_KEY);
    return saved ? JSON.parse(saved) : [];
  });
  const [streamingAnswer, setStreamingAnswer] = useState<{
    thinking: string;
    text: string;
  }>({ thinking: '', text: '' });
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, streamingAnswer]);

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

    const question = input;
    setInput('');
    setChatLoading(true);
    setIsStreaming(true);
    setStreamingAnswer({ thinking: '', text: '' });

    try {
      // 传递清理后的历史对话
      const cleanedHistory = cleanChatHistory(chatHistory);

      // 使用流式请求
      const token = getToken();
      const response = await fetch('/api/ai/advice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: question,
          table_name: tableName,
          history: cleanedHistory,
          stream: true,  // 启用流式输出
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentThinking = '';
      let currentText = '';

      if (!reader) {
        throw new Error('无法读取响应流');
      }

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留最后一个不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              // 流结束，保存到聊天历史
              if (!currentText && !currentThinking) {
                message.warning('未获取到有效响应');
              }
              const finalAnswer = {
                advice: currentText || currentThinking || '未获取到分析结果',
                thinking: currentThinking,
                text: currentText,
              };
              setChatHistory(prev => [...prev, { question, answer: finalAnswer }]);
              setStreamingAnswer({ thinking: '', text: '' });
              setIsStreaming(false);
              setChatLoading(false);
              return;
            }

            try {
              const chunk = JSON.parse(data);

              if (chunk.type === 'thinking') {
                currentThinking += chunk.content || '';
                setStreamingAnswer(prev => ({
                  ...prev,
                  thinking: currentThinking,
                }));
              } else if (chunk.type === 'text') {
                currentText += chunk.content || '';
                setStreamingAnswer(prev => ({
                  ...prev,
                  text: currentText,
                }));
              } else if (chunk.type === 'error') {
                message.error(chunk.content || 'AI分析失败');
                setStreamingAnswer({ thinking: '', text: '' });
                setIsStreaming(false);
                setChatLoading(false);
                return;
              }
            } catch (e) {
              console.error('解析流数据失败:', e, data);
            }
          }
        }
      }
    } catch (e: any) {
      console.error('AI分析失败:', e);
      message.error(e.message || 'AI分析失败');
      setStreamingAnswer({ thinking: '', text: '' });
      setIsStreaming(false);
      setChatLoading(false);
    }
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

  // Generate Report Handler (simplified)
  const handleGenerateReport = async () => {
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
  };

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部控制栏 */}
      <Card bordered={false} style={{ marginBottom: 16, borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <Cascader
            options={cascaderOptions}
            placeholder="请选择要分析的表单数据"
            value={selectedTableArr}
            onChange={setSelectedTableArr}
            expandTrigger="hover"
            style={{ width: 400 }}
            size="large"
          />
          <div style={{ display: 'flex', gap: 12 }}>
            <Button
              type="primary"
              icon={<FileTextOutlined />}
              onClick={handleGenerateReport}
            >生成报告</Button>
            <Button icon={<ClearOutlined />} danger onClick={handleClearChat}>清空</Button>
          </div>
        </div>
      </Card>

      {/* 聊天区域 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        background: '#fff',
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        display: 'flex',
        flexDirection: 'column',
        marginBottom: 16
      }}>
        {chatHistory.length === 0 && !isStreaming ? (
          <div style={{ textAlign: 'center', marginTop: 100, color: '#999' }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16, color: '#e6f4ff' }} />
            <p>请选择左上角的表单，然后开始询问AI分析助手</p>
          </div>
        ) : (
          <>
            {chatHistory.map((item, index) => (
              <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
                {/* User Message */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                  <div style={{
                    background: '#1677ff',
                    color: '#fff',
                    padding: '12px 16px',
                    borderRadius: '12px 12px 0 12px',
                    maxWidth: '80%',
                    boxShadow: '0 2px 6px rgba(22, 119, 255, 0.2)'
                  }}>
                    {item.question}
                  </div>
                  <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} />
                </div>

                {/* AI Message */}
                <div style={{ display: 'flex', justifyContent: 'flex-start', gap: 12 }}>
                  <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
                  <div style={{ maxWidth: '85%' }}>
                    {/* Thinking Process */}
                    {item.answer?.thinking && (
                      <div style={{
                        background: '#f9f9f9',
                        padding: '8px 12px',
                        borderRadius: 8,
                        marginBottom: 8,
                        fontSize: '0.9em',
                        color: '#666',
                        borderLeft: '3px solid #52c41a'
                      }}>
                        <div style={{ fontWeight: 'bold', marginBottom: 4, color: '#52c41a', display: 'flex', alignItems: 'center', gap: 4 }}>
                          💭 思考过程
                        </div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>{item.answer.thinking}</div>
                      </div>
                    )}
                    {/* Final Answer */}
                    <div style={{
                      background: '#f5f5f5',
                      color: '#333',
                      padding: '12px 16px',
                      borderRadius: '0 12px 12px 12px',
                      lineHeight: 1.6
                    }}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>
                        {item.answer?.text || item.answer?.advice || item.answer?.answer || '未获取到分析结果'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Streaming Message */}
            {isStreaming && (
              <div style={{ display: 'flex', justifyContent: 'flex-start', gap: 12, marginBottom: 24 }}>
                <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
                <div style={{ maxWidth: '85%' }}>
                  {streamingAnswer.thinking && (
                    <div style={{
                      background: '#f9f9f9',
                      padding: '8px 12px',
                      borderRadius: 8,
                      marginBottom: 8,
                      fontSize: '0.9em',
                      color: '#666',
                      borderLeft: '3px solid #52c41a'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: 4, color: '#52c41a' }}>💭 思考中...</div>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{streamingAnswer.thinking}</div>
                    </div>
                  )}
                  {(streamingAnswer.text || (!streamingAnswer.thinking && !streamingAnswer.text)) && (
                    <div style={{
                      background: '#f5f5f5',
                      color: '#333',
                      padding: '12px 16px',
                      borderRadius: '0 12px 12px 12px',
                      lineHeight: 1.6
                    }}>
                      {streamingAnswer.text ? (
                        <div style={{ whiteSpace: 'pre-wrap' }}>
                          {streamingAnswer.text}
                          <span style={{ display: 'inline-block', width: 8, height: 16, backgroundColor: '#1890ff', marginLeft: 2, animation: 'blink 1s infinite' }} />
                        </div>
                      ) : (
                        <div style={{ color: '#999' }}><Spin size="small" /> 正在分析数据...</div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 输入框 */}
      <div style={{ background: '#fff', padding: '16px 24px', borderRadius: 12, boxShadow: '0 -2px 12px rgba(0,0,0,0.03)' }}>
        <Input.Search
          value={input}
          onChange={e => setInput(e.target.value)}
          onSearch={handleSend}
          enterButton="发送"
          size="large"
          loading={chatLoading}
          placeholder={selectedTableArr && selectedTableArr.length === 3 ? "请输入你的问题..." : "请先选择上方表单数据"}
          disabled={!selectedTableArr || selectedTableArr.length !== 3 || isStreaming}
        />
      </div>
    </div>
  );
};

export default Chat;
