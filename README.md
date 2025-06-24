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
├── frontend/          # 前端企业级网页（原生JS+Echarts+现代UI）
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

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+（如需前端本地开发）
- MySQL 5.7+
- Redis 5+
- MinIO Server

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置说明
1. 复制`.env.example`为`.env`
2. 配置数据库、Redis、MinIO等信息

### 启动后端服务
```bash
python run.py
```
> 注意：请确保已正确配置.env文件中的数据库、Redis、MinIO等环境变量，否则可能导致连接失败。

### 启动前端服务
- 直接用浏览器打开`frontend/public/index.html`（静态部署）
- 或用Vite/Webpack等工具本地开发

---

## 主要功能
- 🔄 **实时数据采集**：东方财富网多市场、多周期资金流数据
- 📊 **Echarts可视化**：主力资金流、行业/概念/板块趋势
- 💾 **多样化存储**：MySQL结构化、MinIO对象存储、Redis缓存
- 🖥️ **企业级网页**：参数选择、任务状态、动态作图、现代UI
- 🩺 **健康检查接口**：`/api/health`，便于K8s等平台探针

---

## 代码规范与维护
- 完全分层，低耦合高内聚，便于团队协作与扩展
- 日志、异常、配置、健康检查等企业级标准
- 推荐配合CI/CD、Docker、K8s等现代运维体系

---

## 许可证
MIT License
