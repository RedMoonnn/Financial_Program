/**
 * 报告列表Hook
 * 统一管理报告列表的数据获取、删除等操作
 */
import { useState, useEffect, useCallback } from 'react';
import { App } from 'antd';
import axios from 'axios';
import { getErrorMessage } from '../utils/errorHandler';
import { sortByCreatedAt } from '../utils/sortUtils';
import type { ReportFile, ApiResponse } from '../types';

export interface UseReportsOptions {
  /** 是否自动加载 */
  autoLoad?: boolean;
}

/**
 * 报告列表Hook
 * 后端会根据用户权限自动返回相应的数据（管理员看到所有报告，普通用户只看到自己的）
 */
export function useReports(options: UseReportsOptions = {}) {
  const { message } = App.useApp();
  const { autoLoad = true } = options;
  const [reports, setReports] = useState<ReportFile[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取报告列表
  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get<ApiResponse<ReportFile[]>>('/api/v1/report/minio_list');
      if (response.data?.success && Array.isArray(response.data.data)) {
        // 按创建时间倒序排序
        const sorted = sortByCreatedAt(response.data.data, 'desc');
        setReports(sorted);
      } else {
        setReports([]);
      }
    } catch (error: any) {
      const errorMsg = getErrorMessage(error, '获取报告列表失败');
      message.error(errorMsg);
      setReports([]);
    } finally {
      setLoading(false);
    }
  }, [message]);

  // 删除报告
  const deleteReport = useCallback(
    async (fileName: string) => {
      try {
        const res = await axios.delete('/api/v1/report/delete', {
          params: { file_name: fileName },
        });
        if (res.data?.success) {
          message.success(res.data.message || `已删除 ${fileName}`);
          // 刷新列表
          await fetchReports();
          return true;
        } else {
          // 如果响应格式正确但success为false，直接抛出错误让catch处理
          throw new Error(res.data?.message || '删除失败');
        }
      } catch (error: any) {
        const errorMsg = getErrorMessage(error, '删除失败');
        message.error(errorMsg);
        return false;
      }
    },
    [message, fetchReports]
  );

  // 下载报告
  const downloadReport = useCallback((url: string, fileName?: string) => {
    // 如果没有提供文件名，尝试从url中获取（虽然现在后端代理不再依赖url）
    // 为了兼容旧逻辑，我们优先使用文件名调用后端下载接口
    if (fileName) {
      // 使用 fetch 进行下载，以便带上 Authorization 头
      const token = localStorage.getItem('token');
      const downloadUrl = `/api/v1/report/download?file_name=${encodeURIComponent(fileName)}`;

      fetch(downloadUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => {
          if (!response.ok) throw new Error("下载失败");
          return response.blob();
        })
        .then(blob => {
          // 创建临时下载链接
          const blobUrl = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = blobUrl;
          link.download = fileName; // 设置下载文件名
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(blobUrl);
        })
        .catch(err => {
          console.error("Download error:", err);
          message.error("下载失败，请稍后重试");
        });
    } else {
      // 如果没有文件名，回退到打开URL（旧逻辑）
      window.open(url, '_blank');
    }
  }, [message]);

  useEffect(() => {
    if (autoLoad) {
      fetchReports();
    }
  }, [autoLoad, fetchReports]);

  return {
    reports,
    loading,
    fetchReports,
    deleteReport,
    downloadReport,
  };
}
