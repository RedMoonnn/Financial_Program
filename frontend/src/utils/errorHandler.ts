/**
 * 统一错误处理工具函数
 * 从API错误中提取友好的错误消息
 *
 * 后端统一使用 APIResponse 格式：
 * - 成功: {success: true, message: string, data: any}
 * - 失败: {success: false, message: string, code: number, data: any}
 *
 * 异常处理器会返回: {success: false, message: string, code: number, data: any}
 * 其中 message 字段在 detail 中（FastAPI 异常处理）
 */

export interface ApiError {
  response?: {
    data?: {
      // APIResponse 格式
      success?: boolean;
      message?: string;
      code?: number;
      data?: any;
      // FastAPI 异常格式
      detail?: string | { error?: string };
      // 其他可能的错误字段
      msg?: string;
      error?: string;
    };
    status?: number;
  };
  message?: string;
}

/**
 * 从错误对象中提取错误消息
 * @param error 错误对象
 * @param defaultMsg 默认错误消息
 * @returns 友好的错误消息字符串
 */
export function getErrorMessage(error: any, defaultMsg: string = '操作失败'): string {
  if (!error) return defaultMsg;

  const responseData = error.response?.data;

  // 优先处理 APIResponse 格式（后端统一格式）
  if (responseData) {
    // 如果是 APIResponse 格式，直接使用 message 字段
    if (typeof responseData === 'object' && 'success' in responseData && 'message' in responseData) {
      if (responseData.message) {
        return responseData.message;
      }
    }

    // 处理 FastAPI 异常处理器的 detail 字段
    const detail = responseData.detail;
    if (detail) {
      if (typeof detail === 'string') {
        return detail;
      }
      if (typeof detail === 'object' && detail.error) {
        return detail.error;
      }
    }

    // 尝试其他可能的错误字段（兼容旧代码）
    if (responseData.msg) return responseData.msg;
    if (responseData.error) return responseData.error;
    if (responseData.message) return responseData.message;
  }

  // 最后尝试 error.message
  return error.message || defaultMsg;
}
