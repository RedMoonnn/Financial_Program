# dflow 工作流使用指南

## 目录结构

```
dflow_pipeline/
├── __init__.py          # 包初始化
├── config.py            # dflow 配置（自动加载 .env，配置 Argo/MinIO/数据库）
├── run.py               # 工作流启动脚本
├── ops/                 # OP（操作）定义
│   ├── __init__.py
│   ├── crawl_op.py          # 单任务数据采集 OP（已废弃，保留兼容）
│   ├── batch_crawl_op.py    # 批量数据采集 OP（推荐）
│   ├── store_op.py          # 单文件存储 OP（已废弃，保留兼容）
│   ├── batch_store_op.py    # 批量数据存储 OP（推荐）
│   ├── deepseek_analysis_op.py  # DeepSeek AI 分析 OP
│   ├── minio_store_op.py    # MinIO 报告存储 OP
│   ├── ai_op.py             # AI 分析 OP（旧版）
│   └── report_op.py         # 报告生成 OP
└── workflows/           # 工作流定义
    ├── __init__.py
    ├── full_pipeline.py    # 完整流水线（优化版，2 并行任务 + AI 分析）
    ├── incremental.py      # 增量更新流水线
    └── simple_test.py      # 简化版测试流水线（学习用）
```

## 新版流水线架构（v2.0）

```
┌─────────────────────────────────────────────────────────────┐
│              完整流水线 (full) - 优化版                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 并行采集（2 个任务，而非原来的 41 个）               │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │ crawl-stock         │    │ crawl-sector        │        │
│  │ (批量采集 32 组数据) │    │ (批量采集 9 组数据)  │        │
│  └──────────┬──────────┘    └──────────┬──────────┘        │
│             │                          │                    │
│             └────────────┬─────────────┘                    │
│                          │                                  │
│  Step 2: 并行处理（两路）                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  路线 A: 数据库存储                                  │    │
│  │  ┌──────────────┐    ┌──────────────┐              │    │
│  │  │ store-stock  │    │ store-sector │              │    │
│  │  │   → MySQL    │    │   → MySQL    │              │    │
│  │  └──────────────┘    └──────────────┘              │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  路线 B: AI 分析                                     │    │
│  │  ┌──────────────┐    ┌──────────────┐              │    │
│  │  │ ai-analysis  │───▶│store-to-minio│              │    │
│  │  │ DeepSeek API │    │ 报告存MinIO  │              │    │
│  │  └──────────────┘    └──────────────┘              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 环境准备

```bash
# 启动 minikube（如果未启动）
minikube start

# 确保 Argo 和 MinIO 正常运行
kubectl -n argo get pods

# 启动端口转发（dflow 客户端需要）
kubectl -n argo port-forward svc/minio 9000:9000 --address 0.0.0.0 &
kubectl -n argo port-forward svc/argo-server 2746:2746 --address 0.0.0.0 &
```

### 2. 环境变量配置

项目根目录的 `.env` 文件会自动加载：

```bash
# 数据库配置（Pod 内部使用）
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=financial_web_crawler

# MinIO 配置（Pod 内部使用）
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin123
MINIO_BUCKET=data-financial-agent

# DeepSeek AI 配置
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**注意**: dflow 客户端连接 K8s MinIO 使用 `127.0.0.1:9000`（通过端口转发），已在 `config.py` 中配置。

### 3. 运行工作流

```bash
cd /home/chy/dev/Financial_Program/backend

# ===== 生产用的完整工作流 =====

# 完整流水线（采集 + 数据库存储 + AI 分析 + MinIO 报告）
PYTHONPATH=. python -m dflow_pipeline.run full

# 只采集和存储（不进行 AI 分析）
PYTHONPATH=. python -m dflow_pipeline.run crawl

# 增量更新
PYTHONPATH=. python -m dflow_pipeline.run incremental

# 快速刷新
PYTHONPATH=. python -m dflow_pipeline.run quick

# ===== 学习用的简化版工作流 =====

# Hello World（本地调试模式，不需要 K8s）
PYTHONPATH=. python -m dflow_pipeline.run hello --debug

# 简化版爬虫（本地调试模式）
PYTHONPATH=. python -m dflow_pipeline.run simple --debug

# 简化版爬虫（提交到 K8s）
PYTHONPATH=. python -m dflow_pipeline.run simple
```

### 4. 查看工作流状态

```bash
# 查看所有工作流
kubectl -n argo get workflows

# 查看工作流详情
kubectl -n argo get workflow <workflow-name>

# 查看 Pod 日志
kubectl -n argo logs <pod-name> -c main

# 在 Argo UI 中查看（浏览器）
# https://127.0.0.1:2746
```

## 新增 OP 说明

### BatchCrawlStockFlowOP
批量采集所有个股资金流数据（8 市场 × 4 周期 = 32 组），输出单个 JSON 文件。

### BatchCrawlSectorFlowOP
批量采集所有板块资金流数据（3 板块 × 3 周期 = 9 组），输出单个 JSON 文件。

### BatchStoreToMySQLOP
批量存储数据到 MySQL，支持单个文件包含多个表的数据。

### DeepSeekAnalysisOP
使用 DeepSeek API 分析金融数据，生成专业分析报告。

输入:
- `stock_data_file`: 个股数据文件
- `sector_data_file`: 板块数据文件

输出:
- `report_file`: 分析报告 JSON 文件
- `summary`: 简要摘要

### StoreReportToMinIOOP
将分析报告存储到 MinIO，按日期组织目录结构。

输出路径: `analysis_reports/{timestamp}_report.json`

## dflow 核心概念

### 1. OP（Operation）- 操作

OP 是 dflow 的最小执行单元，类似于函数。每个 OP 必须定义：

```python
from dflow.python import OP, OPIO, OPIOSign, Artifact
from pathlib import Path

class MyOP(OP):
    @classmethod
    def get_input_sign(cls):
        """定义输入参数"""
        return OPIOSign({
            "name": str,           # 基本类型
            "count": int,
            "data_file": Artifact(Path),  # 文件类型
        })

    @classmethod
    def get_output_sign(cls):
        """定义输出结果"""
        return OPIOSign({
            "result": str,
            "output_file": Artifact(Path),
        })

    @OP.exec_sign_check  # 自动类型检查
    def execute(self, op_in: OPIO) -> OPIO:
        """执行逻辑"""
        # 获取输入
        name = op_in["name"]

        # 业务逻辑...

        # 返回输出
        return OPIO({
            "result": f"Hello {name}",
            "output_file": Path("/tmp/output.json"),
        })
```

### 2. Template - 模板

Template 将 OP 包装成可以在 K8s 中运行的容器：

```python
from dflow.python import PythonOPTemplate

template = PythonOPTemplate(
    MyOP,                        # OP 类
    image="python:3.9-slim",     # Docker 镜像
    python_packages=[my_dir],    # 上传的 Python 包
    pre_script="pip install requests -q --root-user-action=ignore\n",  # 预安装脚本
)
```

### 3. Step - 步骤

Step 是 Workflow 的执行单元，关联 Template 和参数：

```python
from dflow import Step

step = Step(
    name="my-step",
    template=template,
    parameters={
        "name": "dflow",
        "count": 10,
    },
)
```

### 4. Workflow - 工作流

Workflow 是多个 Step 的组合：

```python
from dflow import Workflow

wf = Workflow(name="my-workflow")
wf.add(step1)
wf.add(step2)
wf.submit()
```

## 执行模式

### Debug 模式（本地）

- 不需要 K8s 集群
- 直接在本地进程中执行
- 适合开发和调试

```python
from dflow import config
config["mode"] = "debug"
```

### K8s 模式（生产）

- 提交到 Argo Workflows
- 在 K8s Pod 中执行
- 支持并行、重试、监控

```python
# 默认模式，不需要额外配置
wf.submit()
```

## 配置说明

### config.py 主要配置

```python
# 自动从项目根目录加载 .env 文件

# Argo Server（本地端口转发）
config["host"] = "https://127.0.0.1:2746"

# dflow S3 配置（本地端口转发连接 K8s MinIO）
s3_config["endpoint"] = "127.0.0.1:9000"
s3_config["access_key"] = "admin"
s3_config["secret_key"] = "password"  # K8s my-minio-cred 中的密码
s3_config["bucket"] = "my-bucket"

# Pod 内部 MySQL 配置（从 .env 加载）
DB_CONFIG = {
    "host": "mysql",
    "port": 3306,
    "database": "financial_web_crawler",
}

# DeepSeek AI 配置（从 .env 加载）
AI_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY"),
    "base_url": "https://api.deepseek.com",
}
```

## 常见问题

### 1. MinIO 连接失败 / 签名不匹配

```bash
# 检查端口转发是否运行
ss -tlnp | grep 9000

# 如果未运行，重新启动
kubectl -n argo port-forward svc/minio 9000:9000 --address 0.0.0.0 &

# 检查 K8s 中的 MinIO 密码
kubectl get secret my-minio-cred -n argo -o yaml
# secretkey 应该是 password (base64: cGFzc3dvcmQ=)
```

### 2. pip root 用户警告

已在所有 `pre_script` 中添加 `--root-user-action=ignore` 参数解决。

### 3. 端口转发断开

```bash
# 重新启动端口转发
kubectl -n argo port-forward svc/minio 9000:9000 --address 0.0.0.0 &
kubectl -n argo port-forward svc/argo-server 2746:2746 --address 0.0.0.0 &
```

### 4. 模块导入失败

```bash
# 确保设置 PYTHONPATH
cd /home/chy/dev/Financial_Program/backend
PYTHONPATH=. python -m dflow_pipeline.run ...
```

### 5. 查看失败原因

```bash
# 查看 Pod 日志
kubectl -n argo logs <pod-name> -c main

# 查看 Workflow 事件
kubectl -n argo describe workflow <workflow-name>
```

## 开发新的 OP

1. 在 `ops/` 目录下创建新文件
2. 继承 `OP` 基类
3. 实现 `get_input_sign`、`get_output_sign`、`execute` 方法
4. 在 `ops/__init__.py` 中添加延迟导入
5. 在 `workflows/` 中创建使用该 OP 的工作流

示例参考：`ops/deepseek_analysis_op.py`
