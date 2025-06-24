import React, { useState } from 'react';
import { Card, Input, Button, List, message } from 'antd';
import axios from 'axios';

const Chat: React.FC = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<{ question: string; answer: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const resp = await axios.post('/api/ai/advice', { message: input });
      setHistory([...history, { question: input, answer: resp.data }]);
      setInput('');
    } catch {
      message.error('对话失败');
    }
    setLoading(false);
  };

  return (
    <Card title="金融智能对话助手" bordered={false}>
      <List
        dataSource={history}
        renderItem={item => (
          <List.Item>
            <div style={{ width: '100%' }}>
              <div style={{ color: '#1677ff', fontWeight: 500 }}>用户：{item.question}</div>
              <div style={{ margin: '8px 0 16px 0', color: '#333' }}>AI：{item.answer}</div>
            </div>
          </List.Item>
        )}
      />
      <Input.TextArea
        value={input}
        onChange={e => setInput(e.target.value)}
        rows={3}
        placeholder="请输入您的问题..."
        style={{ marginTop: 16 }}
      />
      <Button
        type="primary"
        onClick={handleSend}
        loading={loading}
        style={{ marginTop: 8, background: '#1677ff', borderColor: '#1677ff' }}
        block
      >
        发送
      </Button>
    </Card>
  );
};

export default Chat; 