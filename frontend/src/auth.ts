// 认证相关工具函数
import axios from 'axios';

export interface UserInfo {
  id: number;
  email: string;
  username: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string | null;
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function removeToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
}

export function isLogin(): boolean {
  return !!getToken();
}

// 获取用户信息
export async function getUserInfo(): Promise<UserInfo | null> {
  const token = getToken();
  if (!token) return null;

  try {
    // 先尝试从缓存获取
    const cached = localStorage.getItem('userInfo');
    if (cached) {
      return JSON.parse(cached);
    }

    // 从API获取
    const response = await axios.get('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (response.data) {
      localStorage.setItem('userInfo', JSON.stringify(response.data));
      return response.data;
    }
    return null;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    return null;
  }
}

// 检查是否为管理员
export async function isAdmin(): Promise<boolean> {
  const userInfo = await getUserInfo();
  return userInfo?.is_admin === true;
}

// 同步获取用户信息（从缓存）
export function getUserInfoSync(): UserInfo | null {
  const cached = localStorage.getItem('userInfo');
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch {
      return null;
    }
  }
  return null;
}

// 同步检查是否为管理员（从缓存）
export function isAdminSync(): boolean {
  const userInfo = getUserInfoSync();
  return userInfo?.is_admin === true;
}
