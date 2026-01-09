import React, { useState, useEffect, useRef } from 'react';
import { Card, Input, Button, Cascader, Spin, Avatar, App } from 'antd';
import { UserOutlined, RobotOutlined, ClearOutlined, FileTextOutlined, StopOutlined } from '@ant-design/icons';
import axios from 'axios';
import { getToken, getUserInfoSync } from '../auth';
import { getErrorMessage } from '../utils/errorHandler';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ChatProps {
  context?: any;
}

import { cascaderOptions } from '../utils/constants';

const CHAT_HISTORY_KEY_PREFIX = 'financial_chat_history_';
const LAST_USER_ID_KEY = 'last_chat_user_id';

// 获取当前用户的对话历史记录key
const getChatHistoryKey = (userId: number | null): string => {
  if (!userId) return CHAT_HISTORY_KEY_PREFIX + 'guest';
  return CHAT_HISTORY_KEY_PREFIX + userId;
};

const Chat: React.FC<ChatProps> = () => {
  const { message } = App.useApp();
  const [input, setInput] = useState('');
  const [selectedTableArr, setSelectedTableArr] = useState<string[] | undefined>();
  const [chatLoading, setChatLoading] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [streamingAnswer, setStreamingAnswer] = useState<{
    thinking: string;
    text: string;
  }>({ thinking: '', text: '' });
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const autoScrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 初始化：检查用户ID并加载对应的对话历史
  useEffect(() => {
    const userInfo = getUserInfoSync();
    const userId = userInfo?.id || null;

    // 检查用户是否切换
    const lastUserId = localStorage.getItem(LAST_USER_ID_KEY);
    const userIdChanged = lastUserId && lastUserId !== String(userId);

    // 如果用户切换了，立即清空当前显示的对话历史
    if (userIdChanged) {
      setChatHistory([]);
    }

    // 更新当前用户ID
    setCurrentUserId(userId);
    localStorage.setItem(LAST_USER_ID_KEY, String(userId || 'guest'));

    // 加载当前用户的对话历史
    const historyKey = getChatHistoryKey(userId);
    const saved = localStorage.getItem(historyKey);
    if (saved && !userIdChanged) {
      // 只有在用户没有切换的情况下才加载历史记录
      // 如果用户切换了，保持空历史记录
      try {
        setChatHistory(JSON.parse(saved));
      } catch (e) {
        console.error('解析对话历史失败:', e);
        setChatHistory([]);
      }
    } else {
      setChatHistory([]);
    }
  }, []); // 只在组件挂载时执行一次

  // 检查是否在底部附近（允许100px的误差）
  const isNearBottom = (element: HTMLElement) => {
    const threshold = 100;
    return element.scrollHeight - element.scrollTop - element.clientHeight < threshold;
  };

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  // 处理滚动事件
  const handleScroll = () => {
    if (!chatContainerRef.current) return;
    const nearBottom = isNearBottom(chatContainerRef.current);
    // 如果不在底部附近，标记为用户正在滚动查看历史
    setIsUserScrolling(!nearBottom);
  };



  // 聊天记录持久化（保存到当前用户的key）
  useEffect(() => {
    if (currentUserId !== null) {
      const historyKey = getChatHistoryKey(currentUserId);
      localStorage.setItem(historyKey, JSON.stringify(chatHistory));
    }
  }, [chatHistory, currentUserId]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (autoScrollTimeoutRef.current) {
        clearTimeout(autoScrollTimeoutRef.current);
      }
    };
  }, []);

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

  // 用于控制中断请求
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setChatLoading(false);
    setStreamingAnswer({ thinking: '', text: '' });
    // 更新最后一条消息状态，移除 loading 状态（保留已生成的内容或显示已停止）
    setChatHistory(prev => {
      const newHistory = [...prev];
      if (newHistory.length > 0) {
        const lastMsg = newHistory[newHistory.length - 1];
        // 如果已经被标记为完成或错误，就不动了
        // 否则标记为手动停止
        newHistory[newHistory.length - 1] = {
          ...lastMsg,
          answer: {
            ...lastMsg.answer, // 保留已生成的 thinking 和 text
            advice: lastMsg.answer.text || lastMsg.answer.advice || '已停止生成',
          }
        };
      }
      return newHistory;
    });
  };

  const handleSend = async () => {
    // 表名可选
    const tableName = getTableName(selectedTableArr);
    if (!input.trim()) {
      message.warning('请输入问题');
      return;
    }

    const question = input;
    setInput('');

    // 立即将用户问题添加到聊天历史中
    const tempAnswer = { advice: '', thinking: '', text: '' };
    setChatHistory(prev => [...prev, { question, answer: tempAnswer }]);

    setChatLoading(true);
    setIsStreaming(true);
    setStreamingAnswer({ thinking: '', text: '' });
    // 开始流式输出时，如果用户在底部附近，重置滚动标记以允许自动滚动
    if (chatContainerRef.current && isNearBottom(chatContainerRef.current)) {
      setIsUserScrolling(false);
    }

    // 创建新的 AbortController
    abortControllerRef.current = new AbortController();

    // 滚动到底部显示用户问题
    setTimeout(() => {
      scrollToBottom('smooth');
    }, 100);

    try {
      // 传递清理后的历史对话（不包含刚添加的临时消息）
      const cleanedHistory = cleanChatHistory(chatHistory);

      // 使用流式请求
      const token = getToken();
      const response = await fetch('/api/v1/ai/advice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: question,
          table_name: tableName,
          history: cleanedHistory,
          stream: true,
        }),
        signal: abortControllerRef.current?.signal,
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
              // 流结束，更新最后一条消息的答案
              if (!currentText && !currentThinking) {
                message.warning('未获取到有效响应');
              }
              const finalAnswer = {
                advice: currentText || currentThinking || '未获取到分析结果',
                thinking: currentThinking,
                text: currentText,
              };
              // 更新最后一条消息的答案，而不是添加新消息
              setChatHistory(prev => {
                const newHistory = [...prev];
                if (newHistory.length > 0) {
                  newHistory[newHistory.length - 1] = { question, answer: finalAnswer };
                }
                return newHistory;
              });
              setStreamingAnswer({ thinking: '', text: '' });
              setChatLoading(false);
              setIsStreaming(false);
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
                // 实时更新最后一条消息的思考过程
                setChatHistory(prev => {
                  const newHistory = [...prev];
                  if (newHistory.length > 0) {
                    newHistory[newHistory.length - 1] = {
                      question,
                      answer: {
                        advice: currentText || '',
                        thinking: currentThinking,
                        text: currentText,
                      },
                    };
                  }
                  return newHistory;
                });
              } else if (chunk.type === 'text') {
                currentText += chunk.content || '';
                setStreamingAnswer(prev => ({
                  ...prev,
                  text: currentText,
                }));
                // 实时更新最后一条消息的文本内容
                setChatHistory(prev => {
                  const newHistory = [...prev];
                  if (newHistory.length > 0) {
                    newHistory[newHistory.length - 1] = {
                      question,
                      answer: {
                        advice: currentText || '正在回答...',
                        thinking: currentThinking,
                        text: currentText,
                      },
                    };
                  }
                  return newHistory;
                });
              } else if (chunk.type === 'error') {
                message.error(chunk.content || 'AI分析失败');
                // 更新最后一条消息为错误状态
                setChatHistory(prev => {
                  const newHistory = [...prev];
                  if (newHistory.length > 0) {
                    newHistory[newHistory.length - 1] = {
                      question,
                      answer: {
                        advice: `错误: ${chunk.content || 'AI分析失败'}`,
                        thinking: '',
                        text: '',
                      },
                    };
                  }
                  return newHistory;
                });
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

      // 如果循环正常结束但没有收到 [DONE]（虽然不应该发生，但作为兜底）
      setStreamingAnswer({ thinking: '', text: '' });
      setIsStreaming(false);
      setChatLoading(false);
    } catch (e: any) {
      if (e.name === 'AbortError') {
        console.log('生成已因为用户停止而中断');
        setIsStreaming(false);
        setChatLoading(false);
        return;
      }
      console.error('AI分析失败:', e);
      const errorMsg = e.message || 'AI分析失败';
      message.error(errorMsg);
      // 更新最后一条消息为错误状态
      setChatHistory(prev => {
        const newHistory = [...prev];
        if (newHistory.length > 0) {
          newHistory[newHistory.length - 1] = {
            question,
            answer: {
              advice: `错误: ${errorMsg}`,
              thinking: '',
              text: '',
            },
          };
        }
        return newHistory;
      });
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
    if (currentUserId !== null) {
      const historyKey = getChatHistoryKey(currentUserId);
      localStorage.removeItem(historyKey);
    }
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
      const res = await axios.post('/api/v1/report/generate', {
        table_name: getTableName(selectedTableArr),
        chat_history: chatHistory
      });
      hide();
      // 后端返回的是 APIResponse 格式
      if (res.data?.success) {
        message.success(res.data.message || '报告生成成功！');
        window.location.href = '/reports';
      } else {
        message.error(res.data?.message || '报告生成失败');
      }
    } catch (e: any) {
      hide();
      const errorMsg = getErrorMessage(e, '报告生成失败');
      message.error(errorMsg);
    }
  };

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', height: '100%', display: 'flex', flexDirection: 'column' }}>


      {/* 聊天区域 */}
      <div
        ref={chatContainerRef}
        onScroll={handleScroll}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px',
          background: '#fff',
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
          display: 'flex',
          flexDirection: 'column',
          marginBottom: 16
        }}
      >
        {chatHistory.length === 0 && !isStreaming ? (
          <div style={{ textAlign: 'center', marginTop: 100, color: '#999' }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16, color: '#e6f4ff' }} />
            <p>请选择上方的表单，然后开始询问AI分析助手</p>
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
                    {/* Final Answer */}
                    {(item.answer?.text || item.answer?.advice || item.answer?.answer) && (
                      <div style={{
                        background: '#f5f5f5',
                        color: '#333',
                        padding: '12px 16px',
                        borderRadius: '0 12px 12px 12px',
                        lineHeight: 1.6,
                        overflowX: 'auto'
                      }}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ node, inline, className, children, ...props }: any) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  {...props}
                                  style={oneDark}
                                  language={match[1]}
                                  PreTag="div"
                                >
                                  {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                              ) : (
                                <code {...props} className={className} style={{ background: 'rgba(0, 0, 0, 0.06)', padding: '2px 4px', borderRadius: 4, fontFamily: 'monospace' }}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {item.answer?.text || item.answer?.advice || item.answer?.answer || ''}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 输入框 */}
      {/* 顶部控制栏 */}
      <Card variant="borderless" style={{ marginBottom: 16, borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
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

      <div style={{ background: '#fff', padding: '16px 24px', borderRadius: 12, boxShadow: '0 -2px 12px rgba(0,0,0,0.03)' }}>
        <div style={{ display: 'flex', gap: 12 }}>
          {isStreaming ? (
            <Button
              danger
              size="large"
              shape="circle"
              icon={<StopOutlined />}
              onClick={handleStopGeneration}
              title="停止生成"
            />
          ) : null}
          <Input.Search
            value={input}
            onChange={e => setInput(e.target.value)}
            onSearch={handleSend}
            enterButton={isStreaming ? false : "发送"}
            size="large"
            loading={chatLoading}
            placeholder={isStreaming ? "AI正在生成回复..." : "请输入你的问题... (可选：先选择下方表单以分析特定数据)"}
            disabled={isStreaming}
            style={{ flex: 1 }}
          />
        </div>
      </div>
    </div >
  );
};

export default Chat;
