# 东方财富数据采集与分析平台（企业级）

## 项目概述

本项目是一个企业级的前后端分离数据采集与分析平台，专注于从东方财富网获取股票市场数据，支持数据采集、存储、分析、Echarts可视化和网页交互，为投资决策和数据分析提供高效支撑。

---

## 目录结构
```
.
├── backend/           # 后端服务（Flask+SQLAlchemy+Redis+MinIO）
│   ├── api/           # API接口与健康检查
│   ├── crawler/       # 爬虫采集模块
│   ├── services/      # 业务逻辑与服务层
│   ├── models/        # ORM模型
│   ├── storage/       # MinIO存储
│   ├── cache/         # Redis缓存
│   ├── utils/         # 工具函数
│   ├── config.py      # 配置文件
│   └── __init__.py    # 包标识
├── frontend/          # 前端企业级网页（React+Antd+Echarts+现代UI）
│   ├── public/        # 静态资源与入口HTML
│   └── src/           # 前端主逻辑与组件
├── data/              # 数据存储目录（原始数据、图片等，已添加到.gitignore）
├── run.py             # 后端统一启动入口
├── requirements.txt   # Python依赖
├── Dockerfile         # Docker镜像构建
├── docker-compose.yml # 一键部署脚本
└── README.md          # 项目文档
```

---

## 各模块实现原理与关键代码

### backend/api/（API接口与健康检查）
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

### backend/crawler/（爬虫采集模块）
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

### backend/services/（业务逻辑与服务层）
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

### backend/models/（ORM模型）
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

### backend/storage/（MinIO存储）
- 支持图片、报告等大文件的上传与访问。
```python
# backend/storage/storage.py
class MinioStorage:
    def upload_image(self, file_path):
        self.client.fput_object(self.bucket, object_name, file_path)
        return object_name
```

### backend/cache/（Redis缓存）
- 提升热点数据访问速度，支持验证码、会话、数据缓存等。
```python
# backend/cache/cache.py
redis_cache = redis.Redis(host=..., port=..., password=...)
redis_cache.set(key, value, ex=expire)
```

### backend/utils/（工具函数）
- 通用工具函数，如时间处理、环境检测、加密等。
```python
# backend/utils/utils.py
def get_now():
    return datetime.datetime.now()
```

### run.py（后端统一启动入口）
- 自动初始化数据库、启动爬虫定时任务、运行API服务。
```python
from services.services import init_db
init_db()
# 启动爬虫定时任务 ...
uvicorn.run('api.api:app', host='0.0.0.0', port=8000)
```

### frontend/src/（前端主逻辑与组件）
- **多级分类筛选**：
```tsx
// frontend/src/pages/Home.tsx
<Select value={marketType} onChange={setMarketType} options={marketTypes.map(t => ({ label: t, value: t }))} />
```
- **表格与动态图表**：
```tsx
<Table columns={columns} dataSource={tableData} />
<ReactECharts option={chartOption} />
```
- **AI智能对话**：
```tsx
<Chat context={{ marketType, flowType, period, tableData }} />
```
- **用户认证与权限**：
```tsx
<Route path="/login" element={<Login />} />
<Route path="/" element={<PrivateRoute element={<Home />} />} />
```

---

## 其他模块与说明
- **健康检查**：`/api/health`接口，便于K8s等平台探针。
- **退出登录**：前端菜单或按钮点击后清除token并跳转登录页。
- **异常与日志**：后端所有接口均有异常捕获与日志输出，便于排查。

---

## 环境部署与启动方式

### 1. 环境变量配置
- 复制`.env.example`为`.env`，配置如下关键项：
  - MySQL：`MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
  - Redis：`REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD`
  - MinIO：`MINIO_ENDPOINT`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`
  - Deepseek：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`

### 2. 依赖安装
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 3. 本地开发启动
- 启动MySQL、Redis、MinIO服务（可用docker-compose一键启动）
- 启动后端：
  ```bash
  python run.py
  ```
- 启动前端：
  ```bash
  cd frontend
  npm run dev
  # 或 yarn dev
  ```
- 浏览器访问 http://localhost:5173

### 4. Docker一键部署
```bash
docker-compose up --build -d
```
- 自动启动所有服务，端口映射见`docker-compose.yml`。

### 5. 常见问题排查
- 检查.env配置是否正确，数据库/Redis/MinIO/Deepseek服务是否可达。
- 查看`backend/logs/`和前端控制台日志，定位异常。
- 如端口被占用或防火墙限制，调整端口或开放相应端口。

---

## 主要功能
- 🔒 **登录/注册/找回密码为独立页面**：未登录用户只能访问认证相关页面，主功能区完全隔离，登录后可访问全部功能。
- 🔄 **自动化实时数据采集**：后端启动即自动全量爬取东方财富网多市场、多周期资金流数据，定时刷新，数据状态自动提示。
- 📊 **多级分类+Echarts可视化**：前端与后端分类、周期、市场等完全同步，支持多级筛选、表格、动态图表、拖动排序、悬浮提示。
- 🤖 **Deepseek智能分析**：AI对话框可基于当前筛选数据进行专业金融分析，支持上下文多轮追问。
- 💾 **多样化存储**：MySQL结构化、MinIO对象存储、Redis缓存，支持高并发与大数据量。
- 🖥️ **现代企业级UI**：参数选择、任务状态、动态作图、智能对话、退出登录等全流程体验。
- 🩺 **健康检查接口**：`/api/health`，便于K8s等平台探针。

---

## 代码规范与维护
- 完全分层，低耦合高内聚，便于团队协作与扩展
- 日志、异常、配置、健康检查等企业级标准
- 推荐配合CI/CD、Docker、K8s等现代运维体系

---

## 许可证
MIT License
