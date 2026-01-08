# SMTP 邮箱配置指南

## 📧 QQ邮箱 SMTP 配置

### 配置信息

在 `.env` 文件中添加以下配置：

```ini
# =====================================================
# SMTP邮箱配置（用于发送验证码）
# =====================================================
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=chen_hongyue@qq.com
SMTP_PASSWORD=ragbsbnplldhdcjf
```

## 🔑 获取QQ邮箱授权码

QQ邮箱需要使用授权码而不是登录密码。获取方法：

1. 登录QQ邮箱网页版：https://mail.qq.com
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **POP3/SMTP服务** 或 **IMAP/SMTP服务**
5. 点击 **生成授权码**，按提示发送短信验证
6. 将生成的授权码复制保存（这就是 `SMTP_PASSWORD`）

**注意**：授权码只显示一次，请妥善保管！

## 📝 完整配置示例

```ini
# =====================================================
# SMTP邮箱配置（用于发送验证码）
# =====================================================
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=chen_hongyue@qq.com
SMTP_PASSWORD=ragbsbnplldhdcjf
```

## 🌐 其他邮箱服务商配置

### Gmail
```ini
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # 需要使用应用专用密码
```

### 163邮箱
```ini
SMTP_SERVER=smtp.163.com
SMTP_PORT=25  # 或 465 (SSL)
SMTP_USER=your_email@163.com
SMTP_PASSWORD=your_auth_code  # 授权码
```

### 企业邮箱（腾讯企业邮箱）
```ini
SMTP_SERVER=smtp.exmail.qq.com
SMTP_PORT=587
SMTP_USER=your_email@yourdomain.com
SMTP_PASSWORD=your_password
```

## ✅ 验证配置

配置完成后，可以通过以下方式验证：

### 方法1：测试发送验证码

1. 启动应用
2. 访问注册页面或忘记密码页面
3. 输入邮箱地址，点击发送验证码
4. 检查邮箱是否收到验证码邮件

### 方法2：查看日志

如果发送失败，查看应用日志中的错误信息：

```
邮件发送失败: [错误详情]
```

## 🔧 常见问题

### 1. 连接超时

**问题**：`Connection timeout` 或 `Connection refused`

**解决方案**：
- 检查网络连接
- 确认防火墙未阻止 587 端口
- 尝试使用 465 端口（SSL）

### 2. 认证失败

**问题**：`Authentication failed` 或 `535 Login Fail`

**解决方案**：
- 确认使用的是授权码而不是登录密码（QQ邮箱）
- 检查用户名和密码是否正确
- 确认已开启SMTP服务

### 3. SSL/TLS错误

**问题**：`SSL: CERTIFICATE_VERIFY_FAILED`

**解决方案**：
- 代码已使用 `starttls()`，通常不需要额外配置
- 如果仍有问题，可能需要配置SSL证书

### 4. 发送失败但无错误

**问题**：代码执行成功但收不到邮件

**解决方案**：
- 检查垃圾邮件文件夹
- 确认收件人邮箱地址正确
- 检查发送方邮箱是否被限制

## 📚 相关文件

- `backend/services/services.py` - EmailService 实现
- `backend/api/auth.py` - 验证码发送接口

## 🔒 安全建议

1. **保护授权码**：
   - 不要将授权码提交到代码仓库
   - 使用环境变量存储敏感信息
   - 定期更换授权码

2. **限制发送频率**：
   - 代码中已实现验证码5分钟有效期
   - 建议在生产环境添加发送频率限制

3. **监控发送状态**：
   - 记录发送日志
   - 监控失败率
   - 设置告警机制

## 📞 技术支持

如果遇到问题，请检查：
1. `.env` 文件配置是否正确
2. 应用日志中的错误信息
3. 网络连接是否正常
4. 邮箱服务商是否正常
