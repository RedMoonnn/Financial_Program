import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Spin, message } from 'antd';

const EmailPreview: React.FC = () => {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const response = await axios.get('/api/v1/auth/email-preview-template');
        if (response.data?.success && response.data.data?.html) {
          setHtmlContent(response.data.data.html);
        } else {
          message.error('无法加载邮件模版预览');
        }
      } catch (error) {
        console.error('Failed to fetch email template:', error);
        message.error('无法加载邮件模版预览');
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, []);

  if (loading) {
    return (
      <div style={{ width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#333' }}>
        <Spin size="large" tip="加载预览中..." />
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#333', flexDirection: 'column' }}>
      <h2 style={{ color: 'white', marginBottom: 20 }}>邮件模板预览 (Email Template Preview)</h2>
      <div style={{ width: '100%', maxWidth: '800px', height: '80vh', background: '#f3f4f6', borderRadius: 8, overflow: 'hidden' }}>
        <iframe
          srcDoc={htmlContent}
          style={{ width: '100%', height: '100%', border: 'none' }}
          title="Email Preview"
        />
      </div>
    </div>
  );
};

export default EmailPreview;
