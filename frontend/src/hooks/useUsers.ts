/**
 * 用户管理Hook
 * 统一管理用户相关的API调用
 */
import { useState, useEffect, useCallback } from 'react';
import { App } from 'antd';
import axios from 'axios';
import { getErrorMessage } from '../utils/errorHandler';
import type { User } from '../types';

export function useUsers() {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/auth/users');
      // 后端现在返回 APIResponse 格式
      if (response.data?.success && Array.isArray(response.data.data)) {
        setUsers(response.data.data);
      } else {
        setUsers([]);
      }
    } catch (error: any) {
      if (error.response?.status !== 401) {
        const errorMsg = getErrorMessage(error, '获取用户列表失败');
        message.error(errorMsg);
      }
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, [message]);

  const deleteUser = useCallback(
    async (userId: number) => {
      try {
        const response = await axios.delete(`/api/v1/auth/users/${userId}`);
        if (response.data?.success) {
          message.success(response.data.message || '用户已删除');
          await fetchUsers();
          return true;
        } else {
          // 如果响应格式正确但success为false，直接抛出错误让catch处理
          throw new Error(response.data?.message || '删除失败');
        }
      } catch (error: any) {
        const errorMsg = getErrorMessage(error, '删除失败');
        message.error(errorMsg);
        return false;
      }
    },
    [message, fetchUsers]
  );

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return {
    users,
    loading,
    fetchUsers,
    deleteUser,
  };
}
