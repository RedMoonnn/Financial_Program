# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 项目概述

**金融智能数据采集与分析平台** - 企业级金融数据采集、AI分析、可视化展示的全栈应用。

**技术栈核心**:
- **前端**: React 18 + TypeScript + Ant Design 5 + ECharts + Vite
- **后端**: FastAPI + SQLAlchemy 2.0 + Python 3.8+
- **存储**: MySQL 8.0 (结构化数据) + Redis 6.2 (缓存/会话) + MinIO (对象存储)
- **AI**: Deepseek API (大语言模型)
- **部署**: Docker + Docker Compose

---

## 常用命令

### 🐳 Docker Compose 部署 (推荐)

```bash
# 启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]  # backend/frontend/mysql/redis/minio

# 重启服务
docker-compose restart [service_name]

# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会删除数据）
docker-compose down -v
```

### 🔧 后端开发

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器 (自动重载)
python run.py
# 或使用 uvicorn 命令
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 代码检查与格式化
ruff check backend/              # 检查问题
ruff check --fix backend/        # 自动修复
ruff format backend/             # 格式化代码
```

### ⚛️ 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint        # 检查问题
npm run lint:fix    # 自动修复
```

### 🔍 代码质量工具

```bash
# Pre-commit 钩子
pre-commit install              # 安装钩子
pre-commit run --all-files      # 手动运行所有检查
git commit --no-verify          # 跳过钩子提交（不推荐）
```

### 🗄️ 数据库管理

```bash
# 备份 MySQL 数据
docker exec mysql mysqldump -u root -p financial_web_crawler > backup.sql

# 恢复 MySQL 数据
docker exec -i mysql mysql -u root -p financial_web_crawler < backup.sql

# 连接到 MySQL 容器
docker exec -it mysql mysql -u root -p

# 查看 Redis 数据
docker exec -it redis redis-cli -a ${REDIS_PASSWORD}
```

---

## 架构设计与关键概念

### 后端架构分层

系统采用**严格的分层架构**，职责清晰分离：

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (api/v1/endpoints/)                              │
│  职责: HTTP 请求处理、参数验证、响应格式化                    │
│  - 使用 Pydantic 进行请求/响应验证                           │
│  - 路由定义和聚合 (router.py)                                │
│  - 依赖注入 (FastAPI Depends)                                │
├─────────────────────────────────────────────────────────────┤
│  Middleware Layer (api/middleware.py)                       │
│  职责: 跨切面关注点 - 异常处理、日志、CORS                    │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (services/)                                  │
│  职责: 业务逻辑封装，复杂流程编排                             │
│  - services/auth/      用户认证、邮箱验证                    │
│  - services/ai/        AI对话、报告生成                      │
│  - services/flow/      资金流数据查询、图片服务               │
│  - services/report/    报告管理                              │
│  - services/common/    缓存、聊天历史、任务管理               │
├─────────────────────────────────────────────────────────────┤
│  Crawler Layer (crawler/)                                   │
│  职责: 数据采集逻辑，东方财富网爬虫                           │
├─────────────────────────────────────────────────────────────┤
│  ORM Layer (models/models.py)                               │
│  职责: 数据库表定义 (SQLAlchemy declarative models)          │
│  - FlowTask (采集任务)                                       │
│  - FlowData (资金流数据)                                     │
│  - FlowImage (图片URL)                                       │
│  - User (用户表)                                             │
│  - Report (AI报告)                                           │
│  - ChatMessage (聊天历史)                                    │
├─────────────────────────────────────────────────────────────┤
│  Core Layer (core/)                                         │
│  职责: 基础设施封装 - 数据库、缓存、存储、配置                 │
│  - database.py:  SQLAlchemy 会话管理                        │
│  - cache.py:     Redis 连接封装                             │
│  - storage.py:   MinIO 对象存储封装                         │
│  - config.py:    环境变量配置管理                            │
│  - logging.py:   日志配置                                   │
└─────────────────────────────────────────────────────────────┘
```

**核心原则**:
- **单向依赖**: 上层可调用下层，下层不可调用上层
- **依赖注入**: API层通过 FastAPI 的 `Depends()` 注入数据库会话
- **避免循环导入**: Service 层使用 `get_db_session()` 上下文管理器，而非直接依赖注入

### 前端架构模式

前端采用**组件化 + Hooks** 的现代 React 架构：

```
src/
├── pages/              # 页面级组件（路由对应的完整页面）
│   ├── Home.tsx        # 首页：多级Tab数据展示（资金流类型 → 市场 → 周期 → 数据列表）
│   ├── Chat.tsx        # AI对话助手：流式SSE对话 + Markdown渲染
│   ├── Reports.tsx     # 历史报告：MinIO报告列表 + 下载
│   ├── Login.tsx       # 登录：JWT Token + 记住登录
│   ├── Register.tsx    # 注册：邮箱验证码
│   ├── Forgot.tsx      # 找回密码
│   ├── UserCenter.tsx  # 用户中心
│   ├── AdminCollect.tsx   # 管理员：数据采集控制台
│   ├── AdminReports.tsx   # 管理员：报告管理
│   └── AdminUsers.tsx     # 管理员：用户管理
├── hooks/              # 自定义 React Hooks (业务逻辑复用)
│   ├── useCollect.ts   # 数据采集逻辑
│   ├── useReports.ts   # 报告管理逻辑
│   └── useUsers.ts     # 用户管理逻辑
├── types/              # TypeScript 类型定义
├── utils/              # 工具函数
│   ├── apiUtils.ts     # API请求封装 (Axios)
│   ├── dateUtils.ts    # 日期格式化
│   ├── errorHandler.ts # 错误处理
│   └── sortUtils.ts    # 数据排序
└── auth.ts             # 认证工具 (Token管理、权限检查)
```

**数据流模式**:
- **本地状态优先**: 使用 `useState`/`useEffect` 管理组件内状态
- **无全局状态管理库**: 项目规模适中，未引入 Redux/MobX (注：虽然依赖中有 redux，但未在当前代码中使用)
- **API调用**: 统一通过 `utils/apiUtils.ts` 的 `apiRequest()` 函数
- **Token认证**: 存储在 `localStorage`，通过 `auth.ts` 管理

### 数据库会话管理规范

**两种会话模式**:

1. **上下文管理器模式** (Service层推荐):
   ```python
   from core.database import get_db_session

   with get_db_session() as session:
       user = session.query(User).filter_by(email=email).first()
       # 自动 commit/rollback/close
   ```

2. **依赖注入模式** (API层使用):
   ```python
   from core.database import get_db_session_dependency
   from fastapi import Depends
   from sqlalchemy.orm import Session

   @router.get("/users")
   def get_users(db: Session = Depends(get_db_session_dependency)):
       users = db.query(User).all()
       return users
       # FastAPI 自动管理会话生命周期
   ```

**关键注意事项**:
- Service 层**不要使用依赖注入**，因为 Service 可能在非 API 上下文中调用（如定时任务、爬虫）
- 使用 `auto_commit=True`（默认）自动提交，或 `auto_commit=False` 手动控制事务
- 异常会自动触发 `rollback()`，无需手动处理

### AI 流式对话实现

系统使用 **SSE (Server-Sent Events)** 实现流式AI对话：

**后端** (`api/v1/endpoints/ai.py`):
```python
from fastapi.responses import StreamingResponse

@router.post("/advice")
async def ai_advice(request: AdviceRequest):
    async def event_stream():
        async for chunk in deepseek_service.stream_chat(...):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
```

**前端** (`pages/Chat.tsx`):
```typescript
const eventSource = new EventSource('/api/v1/ai/advice');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  setMessages(prev => [...prev, data]);
};
```

**实现细节**:
- 使用 OpenAI SDK 的流式API (`stream=True`)
- 逐块解析 JSON 并通过 SSE 推送
- 前端使用 `EventSource` 接收实时数据
- 支持多轮对话上下文记忆（存储在 `ChatMessage` 表）

### MinIO 报告存储策略

**文件命名规范**:
```
{user_id}/reports/{timestamp}_{table_name}_report.md
```

**权限设计**:
- 用户只能访问自己的报告 (`user_id` 隔离)
- 管理员可以访问所有用户报告
- 使用预签名 URL 实现安全下载

**实现位置**:
- 后端: `core/storage.py` (MinIO 客户端封装)
- 后端: `services/report/report_service.py` (报告CRUD)
- 前端: `pages/Reports.tsx` (报告列表与下载)

### 定时任务调度

使用 **APScheduler** 实现定时数据采集：

**调度器初始化** (`services/scheduler.py`):
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_job(
    func=crawler_job,
    trigger='cron',
    hour='9,15',  # 每天9点和15点执行
    id='daily_crawler'
)
scheduler.start()
```

**生命周期管理** (`app/main.py`):
- 在 FastAPI 的 `lifespan` 事件中初始化
- 应用关闭时自动停止调度器

---

## 开发规范

### Python 代码规范

**遵循 Ruff 配置** (`ruff.toml`):
- 行长度: 100字符
- 启用规则: PEP 8 + pyflakes + isort + bugbear + simplify
- 自动排序导入 (isort)
- 自动格式化 (Ruff formatter)

**类型注解要求**:
```python
# ✅ 推荐：函数签名添加类型注解
def get_user_by_email(email: str, session: Session) -> User | None:
    return session.query(User).filter_by(email=email).first()

# ❌ 避免：缺少类型注解
def get_user_by_email(email, session):
    return session.query(User).filter_by(email=email).first()
```

**异常处理规范**:
```python
# 使用自定义业务异常 (services/exceptions.py)
from services.exceptions import UserNotFoundError, AuthenticationError

# API层捕获并转换为HTTP响应
try:
    user = user_service.authenticate(email, password)
except AuthenticationError as e:
    raise HTTPException(status_code=401, detail=str(e))
```

**数据库查询优化**:
- 使用索引：参考 `models/models.py` 的 `__table_args__`
- 避免 N+1 查询：使用 `joinedload()` 或 `selectinload()`
- 大量数据使用分页：`limit()` + `offset()`

### TypeScript 代码规范

**类型定义要求**:
```typescript
// ✅ 推荐：定义明确的接口
interface FlowDataItem {
  code: string;
  name: string;
  latest_price: number;
  change_percentage: number;
  main_flow_net_amount: number;
}

// ❌ 避免：使用 any
const data: any = await fetchData();
```

**API 调用规范**:
```typescript
// 统一使用 apiUtils.ts 的封装
import { apiRequest } from '../utils/apiUtils';

const response = await apiRequest<FlowDataItem[]>('/api/v1/flow', {
  params: { flow_type, market_type, period }
});
```

**错误处理**:
```typescript
import { handleError } from '../utils/errorHandler';

try {
  const data = await fetchData();
} catch (error) {
  handleError(error, '数据加载失败');
}
```

### Git 提交规范

遵循 **Conventional Commits**:

```bash
# 格式
<类型>(<范围>): <简短描述>

# 示例
feat(ai): 添加流式对话支持
fix(auth): 修复Token过期判断逻辑
refactor(database): 优化会话管理
docs(readme): 更新部署文档
```

**类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `refactor`: 重构（不改变外部行为）
- `perf`: 性能优化
- `docs`: 文档变更
- `test`: 测试相关
- `chore`: 构建/工具/依赖变更

---

## 环境配置

### 环境变量管理

**配置文件**: `.env` (从 `.env.example` 复制)

**关键配置项**:

1. **数据库** (必填):
   ```ini
   MYSQL_HOST=mysql        # Docker环境使用服务名；本地开发使用localhost
   MYSQL_PASSWORD=强密码
   ```

2. **AI服务** (必填):
   ```ini
   DEEPSEEK_API_KEY=sk-xxx  # 从 https://platform.deepseek.com 获取
   ```

3. **JWT认证** (必填):
   ```ini
   JWT_SECRET=随机生成的强密钥  # 使用 openssl rand -hex 32 生成
   ```

4. **管理员账号** (首次启动自动创建):
   ```ini
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=强密码
   ```

5. **SMTP邮箱** (可选，注册/找回密码需要):
   ```ini
   SMTP_SERVER=smtp.qq.com
   SMTP_USER=your@qq.com
   SMTP_PASSWORD=授权码  # 注意是授权码，不是登录密码
   ```

**环境差异**:
- **Docker Compose**: 服务间使用服务名通信 (`mysql`, `redis`, `minio`)
- **本地开发**: 修改为 `localhost`，端口已映射到主机

### 本地开发环境

**仅启动基础设施服务**:
```bash
# 只启动 MySQL, Redis, MinIO
docker-compose up -d mysql redis minio

# 本地运行后端
cd backend && python run.py

# 本地运行前端
cd frontend && npm run dev
```

**注意**: 修改 `.env` 中的服务地址为 `localhost`：
```ini
MYSQL_HOST=localhost
REDIS_HOST=localhost
MINIO_ENDPOINT=localhost:9000
```

---

## 重要文件说明

### 后端关键文件

- **`app/main.py`**: FastAPI 应用入口，生命周期管理（数据库初始化、调度器启动）
- **`api/v1/router.py`**: 路由聚合器，集中注册所有 endpoint
- **`api/middleware.py`**: 全局中间件（异常处理、日志记录）
- **`core/database.py`**: 数据库会话管理，提供 `get_db_session()` 上下文管理器
- **`models/models.py`**: SQLAlchemy ORM 模型定义，包含所有数据表
- **`services/init_db.py`**: 数据库初始化逻辑（建表、创建管理员）
- **`crawler/crawler.py`**: 东方财富网数据爬虫核心逻辑

### 前端关键文件

- **`App.tsx`**: 应用主组件，路由配置、布局管理
- **`pages/Home.tsx`**: 首页多级Tab数据展示，ECharts图表集成
- **`pages/Chat.tsx`**: AI对话助手，SSE流式对话实现
- **`utils/apiUtils.ts`**: Axios封装，统一API请求处理
- **`auth.ts`**: Token管理、用户权限判断

### 配置文件

- **`docker-compose.yml`**: 多容器编排配置
- **`.env.example`**: 环境变量模板
- **`ruff.toml`**: Python 代码检查和格式化配置
- **`vite.config.js`**: Vite构建配置，API代理设置

---

## 常见问题排查

### 数据库连接失败

**症状**: `Can't connect to MySQL server`

**排查**:
1. 检查 MySQL 容器是否启动: `docker-compose ps`
2. 检查健康检查: `docker-compose logs mysql`
3. 确认 `.env` 中密码是否正确
4. 本地开发确认 `MYSQL_HOST=localhost`

### AI 对话无响应

**症状**: 对话请求卡住或报错

**排查**:
1. 检查 Deepseek API Key 是否有效
2. 检查账户余额是否充足
3. 查看后端日志: `docker-compose logs backend | grep ERROR`
4. 确认网络可访问 `https://api.deepseek.com`

### 前端代理失败 (404)

**症状**: API请求返回 404

**排查**:
1. 确认后端服务已启动: `curl http://localhost:8000/docs`
2. 检查 `vite.config.js` 中的 `VITE_API_TARGET` 配置
3. Docker 环境确认为 `http://backend:8000`
4. 本地开发确认为 `http://localhost:8000`

### Redis 连接失败

**症状**: `Connection refused` 或 `Authentication failed`

**排查**:
1. 检查 Redis 密码是否匹配 `.env` 中的 `REDIS_PASSWORD`
2. 确认 Redis 容器启动: `docker-compose ps redis`
3. 测试连接: `docker exec -it redis redis-cli -a ${REDIS_PASSWORD}`

---

## 性能优化建议

### 数据库优化

1. **索引使用**: 已在 `FlowData` 表添加联合索引 `idx_code_type_period_task`
2. **查询优化**: 使用 `limit` 限制返回数据量（参考 `flow_data_query.py`）
3. **连接池**: SQLAlchemy 已启用连接池 (`pool_pre_ping=True`)

### 前端优化

1. **代码分割**: Vite配置中已设置 vendor/antd/echarts 分离
2. **图片懒加载**: ECharts 按需引入
3. **缓存策略**: API响应使用 `Cache-Control` 头（可在 middleware 中添加）

### Redis 缓存策略

**已缓存内容**:
- 用户会话（Token验证）
- 邮箱验证码（5分钟过期）

**建议缓存**:
- 资金流数据查询结果（5分钟过期）
- 热点数据（高频访问的股票代码）

---

## 扩展开发指南

### 添加新的 API 端点

1. 在 `backend/api/v1/endpoints/` 创建新文件（如 `new_feature.py`）
2. 定义路由:
   ```python
   from fastapi import APIRouter

   router = APIRouter()

   @router.get("/new-endpoint")
   def new_endpoint():
       return {"message": "Hello"}
   ```

3. 在 `api/v1/router.py` 中注册:
   ```python
   from api.v1.endpoints import new_feature

   api_router.include_router(new_feature.router, prefix="/new-feature", tags=["new-feature"])
   ```

### 添加新的数据表

1. 在 `models/models.py` 定义模型:
   ```python
   class NewTable(Base):
       __tablename__ = "new_table"
       id = Column(Integer, primary_key=True)
       name = Column(String(64), nullable=False)
   ```

2. 重启应用，数据库自动创建表（由 `init_db()` 处理）

### 添加新的前端页面

1. 在 `frontend/src/pages/` 创建组件（如 `NewPage.tsx`）
2. 在 `App.tsx` 添加路由:
   ```typescript
   <Route path="/new-page" element={<NewPage />} />
   ```

3. 在导航菜单中添加链接

---

## 测试指南

### 后端测试

**测试文件位置**: `backend/tests/`

**运行测试**:
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行所有测试
pytest backend/tests/

# 运行特定测试文件
pytest backend/tests/test_auth.py

# 显示详细输出
pytest -v -s
```

### 前端测试

**当前状态**: 项目暂无前端测试

**推荐添加**:
```bash
# 安装测试库
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# 运行测试
npm run test
```

---

## 安全注意事项

1. **敏感信息保护**:
   - 永远不要将 `.env` 文件提交到 Git
   - 使用 `.gitignore` 排除敏感文件
   - 生产环境使用环境变量或密钥管理服务

2. **SQL 注入防护**:
   - 使用 SQLAlchemy ORM，避免原生 SQL
   - 参数化查询（SQLAlchemy 默认已实现）

3. **XSS 防护**:
   - React 自动转义内容
   - AI 生成内容使用 `react-markdown` 渲染（已配置安全选项）

4. **认证安全**:
   - JWT Token 有效期设置（默认7天）
   - 密码使用 bcrypt 加密存储
   - Redis 会话管理

---

## 相关文档

项目根目录的 `README.md` 提供了完整的项目介绍、功能说明和快速开始指南。

`docs/` 目录包含以下专题文档:
- `docker_compose_guide.md`: Docker Compose 部署详解
- `service_ports_guide.md`: 服务端口说明
- `stress_testing_guide.md`: 压力测试指南

---

## 联系与支持

- **邮箱**: 3188018553@qq.com
- **QQ群**: 3188018553
- **GitHub Issues**: 提交Bug或功能建议
