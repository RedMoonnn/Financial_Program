/**
 * API 响应处理工具函数
 * 统一处理后端 APIResponse 格式的响应
 */

import { message } from 'antd';
import { getErrorMessage } from './errorHandler';

/**
 * APIResponse 格式定义（与后端保持一致）
 */
export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  code?: number;
}

/**
 * 处理 API 响应，统一检查 success 字段
 * @param response axios 响应对象
 * @param onSuccess 成功回调
 * @param onError 错误回调（可选）
 * @returns 返回 data 字段，如果失败则抛出错误
 */
export function handleAPIResponse<T = any>(
  response: { data: APIResponse<T> },
  onSuccess?: (data: T) => void,
  onError?: (errorMsg: string) => void
): T {
  if (response.data?.success && response.data.data !== undefined) {
    onSuccess?.(response.data.data);
    return response.data.data;
  } else {
    const errorMsg = response.data?.message || '操作失败';
    onError?.(errorMsg);
    throw new Error(errorMsg);
  }
}

/**
 * 处理 API 响应（不抛出错误，返回结果对象）
 * @param response axios 响应对象
 * @returns {success: boolean, data?: T, message?: string}
 */
export function handleAPIResponseSafe<T = any>(
  response: { data: APIResponse<T> }
): { success: boolean; data?: T; message?: string } {
  if (response.data?.success) {
    return {
      success: true,
      data: response.data.data,
      message: response.data.message,
    };
  } else {
    return {
      success: false,
      message: response.data?.message || '操作失败',
    };
  }
}

/**
 * 带错误提示的 API 调用包装器
 * @param apiCall API 调用函数
 * @param options 配置选项
 * @returns Promise<T>
 */
export async function callAPIWithErrorHandling<T = any>(
  apiCall: () => Promise<{ data: APIResponse<T> }>,
  options?: {
    successMsg?: string;
    errorMsg?: string;
    showSuccess?: boolean;
    showError?: boolean;
  }
): Promise<T> {
  const {
    successMsg,
    errorMsg = '操作失败',
    showSuccess = false,
    showError = true,
  } = options || {};

  try {
    const response = await apiCall();
    if (response.data?.success) {
      if (showSuccess && successMsg) {
        message.success(successMsg || response.data.message);
      }
      return response.data.data as T;
    } else {
      const errMsg = response.data?.message || errorMsg;
      if (showError) {
        message.error(errMsg);
      }
      throw new Error(errMsg);
    }
  } catch (error: any) {
    const errMsg = getErrorMessage(error, errorMsg);
    if (showError) {
      message.error(errMsg);
    }
    throw error;
  }
}
