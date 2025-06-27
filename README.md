# 💹 东方财富数据采集与分析平台（企业级）

## 📑 目录

- [项目概述](#项目概述)
- [系统架构](#系统架构)
- [前端结构](#前端结构)
  - [核心组件](#核心组件)
  - [页面结构](#页面结构)
  - [状态管理](#状态管理)
- [后端结构](#后端结构)
  - [API接口](#api接口)
  - [服务模块](#服务模块)
  - [数据模型](#数据模型)
- [核心功能](#核心功能)
  - [数据采集与分析](#数据采集与分析)
  - [AI智能分析](#ai智能分析)
  - [用户与权限系统](#用户与权限系统)
- [部署说明](#部署说明)
- [技术栈](#技术栈)

## 📋 项目概述

东方财富数据采集与分析平台是一个面向企业级金融数据需求的全流程解决方案，集成了自动化数据采集、结构化存储、AI智能分析、可视化展示和权限管理等功能。平台支持多市场、多周期、多分类的资金流数据采集，结合大模型AI分析，为投资决策和数据洞察提供强大支撑。

![系统概览](https://cdn.pixabay.com/photo/2017/01/06/19/15/chart-1953616_960_720.jpg)

## 🏗️ 系统架构

平台采用前后端分离架构，支持容器化部署，具备高可用、易维护、易扩展等企业级特性。

```mermaid
flowchart TD
  subgraph Frontend [用户浏览器]
    F1[React + Ant Design + Echarts]
    F2[多级分类筛选]
    F3[表格/动态图表]
    F4[AI智能对话框]
    F5[用户认证/权限]
  end
  subgraph Backend [FastAPI Service]
    B1[API接口层]
    B2[爬虫采集模块]
    B3[业务服务层]
    B4[AI分析(Deepseek)]
    B5[健康检查]
  end
  subgraph Storage
    D1[(MySQL)]
    D2[(Redis)]
    D3[(MinIO)]
  end
  F1 -->|RESTful API| B1
  F2 --> F1
  F3 --> F1
  F4 --> F1
  F5 --> F1
  B1 -->|数据查询/采集/AI分析| B2
  B1 -->|业务逻辑| B3
  B1 -->|AI对话| B4
  B1 -->|健康检查| B5
  B2 -->|采集数据| B3
  B3 -->|入库/查询| D1
  B3 -->|缓存| D2
  B3 -->|文件存储| D3
  B4 -->|AI分析| F4
  F1 <-->|Token校验| B1
  F5 -->|登录/注册/权限| B1
  B1 -->|认证/权限| D2
```

### 数据流向

```
用户请求 → 前端UI → API请求 → 后端服务 → 数据库/AI分析 → 返回结果 → 前端渲染 → 用户界面展示
```

---

## 🖥️ 前端结构

前端采用React + TypeScript开发，结合Ant Design和Echarts实现现代化企业级UI和数据可视化。

### 目录结构

```
frontend/
├── public/          # 静态资源
├── src/
│   ├── assets/      # 图片、图标等资源
│   ├── components/  # 可复用组件
│   ├── pages/       # 页面组件
│   ├── store.ts     # 状态管理
│   ├── App.tsx      # 主应用组件
│   └── main.tsx     # 应用入口
└── package.json     # 依赖配置
```

### 核心组件

#### 📊 DataTable 组件
- 多级分类筛选与表格展示，支持排序、拖拽、悬浮提示。
- 实时与后端数据同步。

#### 📈 EchartsPanel 组件
- 动态资金流趋势图，支持多市场、多周期切换。
- 交互式图表，支持缩放、筛选。

#### 🤖 DeepseekChat 组件
- 集成AI智能分析对话，自动获取当前筛选数据。
- 支持多轮追问和专业金融分析。

#### 🧭 Navbar/Menu 组件
- 权限控制，登录/注册/找回密码独立页面。
- 用户中心与主功能区分离。

### 页面结构

- 🏠 **Home**: 平台首页与数据总览
- 💬 **Chat**: AI智能分析页面
- 📊 **Reports**: 资金流报告与可视化
- 👤 **UserCenter**: 用户信息与权限管理
- 🔐 **Login/Register/Forgot**: 认证相关页面

### 状态管理
- Token持久化，切换菜单不丢失登录态。
- 权限路由守卫，未登录用户仅可访问认证页面。
- 退出登录按钮，清除token并跳转登录页。

---

## 🖧 后端结构

后端基于FastAPI开发，采用分层解耦设计，支持高并发与大数据量处理。

### 目录结构

```
backend/
├── api/         # API接口与健康检查
├── crawler/     # 爬虫采集模块
├── services/    # 业务逻辑与服务层
├── models/      # ORM模型
├── storage/     # MinIO存储
├── cache/       # Redis缓存
├── utils/       # 工具函数
├── run.py       # 启动入口
└── requirements.txt # 依赖配置
```

### 主要模块与实现原理

#### 📡 api/（API接口与健康检查）
- 提供RESTful接口，负责数据查询、采集任务、AI分析、用户认证、健康检查等。
- 典型接口实现：
```python
# backend/api/api.py
@app.get("/api/flow")
async def get_flow(code: Optional[str] = Query(None), flow_type: str = Query(...), market_type: str = Query(...), period: str = Query(...)):
    from services.services import SessionLocal, FlowData
    session = SessionLocal()
    if code:
        data = session.query(FlowData).filter_by(code=code, flow_type=flow_type, market_type=market_type, period=period).all()
    else:
        data = session.query(FlowData).filter_by(flow_type=flow_type, market_type=market_type, period=period).all()
    session.close()
    return {"data": [d.to_dict() for d in data]}
```

#### 🕸️ crawler/（爬虫采集模块）
- 自动遍历东方财富网各市场、周期、分类，解析资金流数据。
- 支持定时任务和异常重试。
```python
# backend/crawler/crawler.py
def fetch_flow_data(flow_type, market_type, period, pages=1):
    results = []
    for page in range(1, int(pages)+1):
        params = {"pn": page, "pz": 50}
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        # ...解析数据...
        for diff in diff_list:
            item = { 'code': diff['f12'], 'name': diff['f14'], ... }
            results.append(item)
    return results
```

#### 🧩 services/（业务逻辑与服务层）
- 负责数据入库、缓存、AI分析、用户管理、报告生成等核心逻辑。
```python
# backend/services/services.py
class FlowDataService:
    @staticmethod
    def save_flow_data(data_list, task_id):
        session = SessionLocal()
        for data in data_list:
            flow_data = FlowData(**data, task_id=task_id)
            session.merge(flow_data)
        session.commit()
        session.close()
```

#### 🗄️ models/（ORM模型）
- 定义所有数据库表结构，支持高效查询与索引。
```python
# backend/models/models.py
class FlowData(Base):
    __tablename__ = 'flow_data'
    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    # ... 其他字段 ...
```

#### ☁️ storage/（MinIO存储）
- 支持图片、报告等大文件的上传与访问。
```python
# backend/storage/storage.py
class MinioStorage:
    def upload_image(self, file_path):
        self.client.fput_object(self.bucket, object_name, file_path)
        return object_name
```

#### ⚡ cache/（Redis缓存）
- 提升热点数据访问速度，支持验证码、会话、数据缓存等。
```python
# backend/cache/cache.py
redis_cache = redis.Redis(host=..., port=..., password=...)
redis_cache.set(key, value, ex=expire)
```

#### 🛠️ utils/（工具函数）
- 通用工具函数，如时间处理、环境检测、加密等。
```python
# backend/utils/utils.py
def get_now():
    return datetime.datetime.now()
```

#### 🚀 run.py（后端统一启动入口）
- 自动初始化数据库、启动爬虫定时任务、运行API服务。
```python
from services.services import init_db
init_db()
# 启动爬虫定时任务 ...
uvicorn.run('api.api:app', host='0.0.0.0', port=8000)
```

### API接口

#### 🔒 auth.py
- 用户注册、登录、找回密码、邮箱验证、权限校验

#### 📈 api.py
- 资金流数据查询、批量查询、数据状态检测
- AI分析接口，支持context参数

#### 🩺 health.py
- 健康检查接口，便于K8s等平台探针

### 服务模块

#### 🕸️ 爬虫采集服务
- 自动全量爬取东方财富网多市场、多周期资金流数据
- 定时刷新，异常重试，数据入库

#### 🧠 Deepseek AI分析服务
- 调用Deepseek大模型API，基于当前表格数据生成专业分析
- 日志与异常处理，API KEY安全管理

#### 💾 存储与缓存服务
- MySQL结构化存储，MinIO对象存储，Redis缓存
- 支持高并发与大数据量

### 数据模型
- FlowData、User、Task等核心表结构，支持高效查询与索引

---

## 🔑 核心功能

### 数据采集与分析
1. 后端启动自动全量采集东方财富网资金流数据，支持多市场、多周期、多分类
2. 定时刷新，数据状态自动提示，前端页面加载时检测数据是否准备好
3. 支持批量查询与多级筛选，适配表格和动态图表

### AI智能分析
1. Deepseek对话框集成主页面，自动获取当前筛选数据
2. 支持多轮追问和专业金融分析，返回详细投资建议
3. 后端AI接口支持context参数，基于当前数据做针对性分析

### 用户与权限系统
1. 登录/注册/找回密码为独立页面，主功能区需登录后访问
2. 支持管理员账号自动创建，权限分级管理
3. Token持久化，安全认证，退出登录一键清除

---

## 🚀 部署说明

### 环境变量配置
- 复制`.env.example`为`.env`，配置MySQL、Redis、MinIO、Deepseek等服务连接信息

### 依赖安装
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 本地开发启动
```bash
# 启动MySQL、Redis、MinIO（可用docker-compose）
python run.py  # 启动后端
cd frontend && npm run dev  # 启动前端
# 浏览器访问 http://localhost:5173
```

### Docker一键部署
```bash
docker-compose up --build -d
```
- 自动启动所有服务，端口映射见`docker-compose.yml`

### 常见问题排查
- 检查.env配置、服务可达性、端口防火墙、日志定位异常

---

## 💻 技术栈

### 前端技术
- ⚛️ **React** + **TypeScript**：企业级UI与类型安全
- 🐜 **Ant Design**：现代UI组件库
- 📊 **Echarts**：金融数据可视化
- 🔄 **Token持久化/权限路由**：安全认证

### 后端技术
- 🚀 **FastAPI**：高性能API框架
- 🐍 **Python**：主力开发语言
- 📊 **SQLAlchemy**：ORM数据库操作
- 🧠 **Deepseek**：AI智能分析服务
- 💾 **MySQL/Redis/MinIO**：多样化存储
- 🐳 **Docker/docker-compose**：一键部署

---

📌 **系统特点：**
- 🎯 面向企业级金融数据采集与分析全流程
- 🧠 集成AI大模型，智能分析与投资建议
- 📊 多级分类、动态图表、实时数据同步
- 🔒 完善权限认证与安全机制
- 🩺 健康检查、日志监控、CI/CD、容器化最佳实践
如需详细二次开发、运维或企业定制支持，请查阅源码注释与文档，或联系项目维护者。

