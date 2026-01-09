/**
 * 排序工具函数
 */

/**
 * 按创建时间排序
 * @param items 待排序的数组
 * @param order 排序顺序，'desc' 降序（最新的在前），'asc' 升序
 * @returns 排序后的新数组
 */
export function sortByCreatedAt<T extends { created_at?: string | null }>(
  items: T[],
  order: 'asc' | 'desc' = 'desc'
): T[] {
  return [...items].sort((a, b) => {
    const aTime = a.created_at;
    const bTime = b.created_at;

    // 有时间的排在前面
    if (aTime && bTime) {
      const comparison = aTime.localeCompare(bTime);
      return order === 'desc' ? -comparison : comparison;
    } else if (aTime) {
      return -1;
    } else if (bTime) {
      return 1;
    } else {
      return 0;
    }
  });
}
