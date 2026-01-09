/**
 * 统一类型定义
 */

// 用户信息类型（与后端 UserOut 保持一致）
export interface User {
  id: number;
  email: string;
  username: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string | null;
}

export interface ReportFile {
  file_name: string;
  url: string;
  created_at?: string;
  user_id?: number;
  user_email?: string;
  username?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  code?: number;
}
