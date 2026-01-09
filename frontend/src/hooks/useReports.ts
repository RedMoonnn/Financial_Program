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
  const downloadReport = useCallback((url: string) => {
    window.open(url, '_blank');
  }, []);

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
