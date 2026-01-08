# 管理员账号配置指南

## 📋 配置说明

管理员账号通过环境变量自动创建，配置在 `.env` 文件中。

## ⚙️ 环境变量配置

在 `.env` 文件中添加以下配置：

```ini
# =====================================================
# 管理员账号配置
# =====================================================
ADMIN_EMAIL=admin@example.com          # 管理员邮箱（必填）
ADMIN_PASSWORD=your_secure_password     # 管理员密码（必填，建议使用强密码）
ADMIN_USERNAME=admin                    # 管理员用户名（可选，默认为"admin"）
```

## 🔐 安全建议

1. **密码强度**：
   - 至少包含大小写字母和数字
   - 长度建议 12 位以上
   - 不要使用常见密码

2. **邮箱配置**：
   - 使用真实可用的邮箱地址
   - 用于接收验证码和重要通知

3. **用户名配置**：
   - 如果不配置 `ADMIN_USERNAME`，默认使用 "admin"
   - 建议使用有意义的用户名

## 📝 配置示例

```ini
# =====================================================
# 管理员账号配置
# =====================================================
ADMIN_EMAIL=admin@financial.com
ADMIN_PASSWORD=SecurePass123!@#
ADMIN_USERNAME=admin
```

## 🚀 自动创建流程

1. 应用启动时，`init_db()` 函数会自动检查环境变量
2. 如果配置了 `ADMIN_EMAIL` 和 `ADMIN_PASSWORD`，会自动创建管理员账号
3. 如果管理员账号已存在，会确保 `is_admin` 标志正确设置
4. 创建成功后会输出日志：`已自动创建管理员账号: admin@example.com (username: admin)`

## 🔑 管理员权限

管理员账号具有以下权限：

### ✅ 管理员专属功能

1. **数据采集**：
   - `/api/collect_v2` - 单组合数据采集
   - `/api/collect_all_v2` - 全量数据采集

2. **报告管理**：
   - `/api/report/minio_list` - 查看所有报告文件
   - `/api/report/delete` - 删除报告文件

### 📊 普通用户功能（管理员也可使用）

1. **报告操作**：
   - `/api/report/list` - 查看自己的报告列表
   - `/api/report/download` - 下载报告
   - `/api/report/generate` - 生成报告
   - `/api/report/history` - 查看报告历史

2. **其他功能**：
   - `/api/flow` - 查看资金流数据
   - `/api/ai/advice` - AI 分析建议

## 🔍 验证管理员账号

### 方法 1：通过数据库查询

```sql
SELECT id, email, username, is_admin, created_at
FROM user
WHERE is_admin = 1;
```

### 方法 2：通过 API 测试

使用管理员账号登录后，尝试访问需要管理员权限的接口：

```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# 使用 token 访问管理员接口（应该成功）
curl -X GET http://localhost:8000/api/report/minio_list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

如果返回 403 错误，说明不是管理员账号。

## ⚠️ 注意事项

1. **首次配置**：首次启动应用时，确保 `.env` 文件中的管理员配置正确
2. **密码安全**：生产环境务必使用强密码，不要使用默认密码
3. **权限检查**：所有需要管理员权限的接口都会自动检查 `is_admin` 字段
4. **数据库迁移**：如果已有数据库，需要手动添加 `is_admin` 字段或重新创建表

## 🛠️ 手动设置管理员

如果需要在已有数据库中手动设置管理员：

```sql
-- 将指定用户设置为管理员
UPDATE user SET is_admin = 1 WHERE email = 'admin@example.com';

-- 查看所有管理员
SELECT email, username, is_admin FROM user WHERE is_admin = 1;
```

## 📚 相关文件

- `backend/models/models.py` - User 模型定义（包含 `is_admin` 字段）
- `backend/services/services.py` - 管理员创建逻辑（`init_db` 函数）
- `backend/api/auth.py` - 权限验证函数（`get_admin_user`）
