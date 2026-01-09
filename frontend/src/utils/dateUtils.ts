/**
 * 日期格式化工具函数
 */
import dayjs from 'dayjs';

/**
 * 格式化日期时间
 * @param date 日期字符串或null/undefined
 * @param format 格式类型：'full' 完整格式, 'date' 仅日期, 'local' 本地化格式
 * @returns 格式化后的日期字符串，如果为空则返回 '-'
 */
export function formatDateTime(
  date: string | null | undefined,
  format: 'full' | 'date' | 'local' = 'full'
): string {
  if (!date) return '-';
  try {
    if (format === 'local') {
      return new Date(date).toLocaleString('zh-CN');
    }
    if (format === 'date') {
      return dayjs(date).format('YYYY-MM-DD');
    }
    return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
  } catch {
    return '-';
  }
}

/**
 * 格式化日期
 * @param date 日期字符串或null/undefined
 * @returns 格式化后的日期字符串，如果为空则返回 '-'
 */
export function formatDate(date: string | null | undefined): string {
  return formatDateTime(date, 'date');
}

/**
 * 格式化日期时间为本地化格式
 * @param date 日期字符串或null/undefined
 * @returns 格式化后的日期字符串，如果为空则返回 '-'
 */
export function formatDateTimeLocal(date: string | null | undefined): string {
  return formatDateTime(date, 'local');
}
