/**
 * 数据采集Hook
 * 统一管理数据采集相关的API调用
 */
import { useState, useCallback } from 'react';
import { App } from 'antd';
import axios from 'axios';
import { getErrorMessage } from '../utils/errorHandler';

export interface CollectParams {
  flow_choice: number;
  market_choice?: number;
  detail_choice?: number;
  day_choice: number;
  pages?: number;
}

export interface CollectResult {
  table: string;
  count: number;
  crawl_time: string;
  data: any[];
}

/**
 * 单组合数据采集Hook
 */
export function useSingleCollect() {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);

  const execute = useCallback(
    async (params: CollectParams) => {
      setLoading(true);
      try {
        const response = await axios.post('/api/v1/collect/collect_v2', params);
        if (response.data?.success) {
          return response.data;
        } else {
          // 如果响应格式正确但success为false，直接抛出错误让catch处理
          throw new Error(response.data?.message || '采集失败');
        }
      } catch (error: any) {
        const errorMsg = getErrorMessage(error, '采集失败');
        message.error(errorMsg);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [message]
  );

  return { execute, loading };
}

/**
 * 全量数据采集Hook
 */
export function useCollectAll() {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);

  const execute = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/collect/collect_all_v2');
      if (response.data?.success) {
        message.success(response.data.message || '全量采集任务已启动，正在后台执行...');
        return response.data;
      } else {
        // 如果响应格式正确但success为false，直接抛出错误让catch处理
        throw new Error(response.data?.message || '启动全量采集失败');
      }
    } catch (error: any) {
      const errorMsg = getErrorMessage(error, '启动全量采集失败');
      message.error(errorMsg);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [message]);

  return { execute, loading };
}
