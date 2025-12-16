# dflow 操作指南

本文档提供 dflow 工作流的详细操作方法。

---

## 1. 环境安装

### 1.1 安装 Minikube (本地 Kubernetes)

```bash
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Windows (使用 PowerShell 管理员模式)
choco install minikube
```

### 1.2 启动 Kubernetes 集群

```bash
# 启动 minikube (建议至少 4GB 内存)
minikube start --memory 4096 --cpus 4

# 验证集群状态
kubectl cluster-info
kubectl get nodes
```

### 1.3 安装 Argo Workflows

```bash
# 创建 argo 命名空间
kubectl create ns argo

# 安装 dflow 快速启动配置 (包含 Argo + MinIO + PostgreSQL)
kubectl apply -n argo -f https://raw.githubusercontent.com/deepmodeling/dflow/master/manifests/quick-start-postgres.yaml

# 等待所有 Pod 就绪 (约 2-5 分钟)
kubectl -n argo get pods -w

# 确认所有 Pod 状态为 Running
kubectl -n argo get pods
```

### 1.4 端口转发

```bash
# Argo Server UI (访问 https://127.0.0.1:2746)
kubectl -n argo port-forward deployment/argo-server 2746:2746 --address 0.0.0.0 &

# MinIO Console (访问 http://127.0.0.1:9001)
kubectl -n argo port-forward deployment/minio 9000:9000 9001:9001 --address 0.0.0.0 &
```

### 1.5 安装 Python 依赖

```bash
cd /path/to/Financial_Program/backend
pip install pydflow
```

---

## 2. 运行工作流

### 2.1 命令行方式

```bash
cd /path/to/Financial_Program/backend

# 运行完整流水线 (41 个并行任务)
python -m dflow_pipeline.run full

# 运行增量更新 (11 个并行任务，只采集 today)
python -m dflow_pipeline.run incremental

# 运行快速刷新 (1 个任务，只采集全部A股 today)
python -m dflow_pipeline.run quick

# 本地调试模式 (不需要 K8s，纯 Python 执行)
python -m dflow_pipeline.run debug
```

### 2.2 Python 代码方式

```python
from dflow_pipeline.workflows.full_pipeline import create_full_pipeline
from dflow_pipeline.workflows.incremental import create_incremental_pipeline

# 创建并提交完整流水线
wf = create_full_pipeline()
wf.submit()
print(f"Workflow ID: {wf.id}")

# 创建并提交增量更新
wf = create_incremental_pipeline()
wf.submit()

# 等待工作流完成
wf.wait()

# 获取工作流状态
print(f"Status: {wf.status}")
```

### 2.3 调试模式

```python
from dflow import config

# 启用调试模式 (本地执行，不需要 K8s)
config["mode"] = "debug"

from dflow_pipeline.workflows.incremental import create_incremental_pipeline

wf = create_incremental_pipeline()
wf.submit()  # 将在本地执行
```

---

## 3. 监控工作流

### 3.1 Argo UI

访问 https://127.0.0.1:2746 查看工作流状态：

- **Workflows**: 查看所有工作流列表
- **Workflow Details**: 查看单个工作流的 DAG 图和步骤状态
- **Logs**: 查看每个步骤的日志输出
- **Artifacts**: 查看和下载工作流产出的文件

### 3.2 命令行监控

```bash
# 查看所有工作流
kubectl -n argo get workflows

# 查看工作流详情
kubectl -n argo describe workflow <workflow-name>

# 查看工作流日志
kubectl -n argo logs <pod-name>

# 实时查看工作流状态
kubectl -n argo get workflows -w
```

### 3.3 Python API 监控

```python
from dflow import Workflow

# 获取工作流状态
wf = Workflow.from_id("workflow-id")
print(f"Status: {wf.status}")
print(f"Phase: {wf.phase}")

# 获取步骤状态
for step in wf.steps:
    print(f"{step.name}: {step.phase}")

# 获取输出 artifacts
outputs = wf.query_step("crawl-stock")[0].outputs.artifacts
print(outputs)
```

---

## 4. 定时任务

### 4.1 创建 CronWorkflow

创建文件 `cron-workflow.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata:
  name: financial-cron
  namespace: argo
spec:
  schedule: "*/5 * * * *"  # 每 5 分钟执行
  timezone: "Asia/Shanghai"
  concurrencyPolicy: Replace  # 新任务替换旧任务
  startingDeadlineSeconds: 60
  workflowSpec:
    entrypoint: main
    templates:
      - name: main
        container:
          image: python:3.9-slim
          command: ["python", "-c"]
          args:
            - |
              import sys
              sys.path.insert(0, '/app')
              from dflow_pipeline.workflows.incremental import create_incremental_pipeline
              wf = create_incremental_pipeline()
              wf.submit()
          volumeMounts:
            - name: app-code
              mountPath: /app
          env:
            - name: MYSQL_HOST
              value: "mysql-service"
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secrets
                  key: password
    volumes:
      - name: app-code
        configMap:
          name: financial-code
```

### 4.2 应用定时任务

```bash
# 创建定时任务
kubectl apply -f cron-workflow.yaml

# 查看定时任务
kubectl -n argo get cronworkflows

# 查看定时任务详情
kubectl -n argo describe cronworkflow financial-cron

# 手动触发一次
kubectl -n argo create workflow --from=cronworkflow/financial-cron

# 暂停定时任务
kubectl -n argo patch cronworkflow financial-cron -p '{"spec":{"suspend":true}}'

# 恢复定时任务
kubectl -n argo patch cronworkflow financial-cron -p '{"spec":{"suspend":false}}'

# 删除定时任务
kubectl -n argo delete cronworkflow financial-cron
```

---

## 5. 故障排查

### 5.1 常见问题

#### Pod 无法启动

```bash
# 查看 Pod 状态
kubectl -n argo get pods

# 查看 Pod 事件
kubectl -n argo describe pod <pod-name>

# 常见原因：
# - ImagePullBackOff: 镜像拉取失败，检查网络或镜像名
# - CrashLoopBackOff: 容器启动后崩溃，查看日志
# - Pending: 资源不足，检查节点资源
```

#### 工作流失败

```bash
# 查看工作流状态
kubectl -n argo get workflow <workflow-name> -o yaml

# 查看失败步骤的日志
kubectl -n argo logs <pod-name> -c main

# 重新提交失败的工作流
kubectl -n argo resubmit <workflow-name>
```

#### MinIO 连接失败

```bash
# 检查 MinIO Pod 状态
kubectl -n argo get pods | grep minio

# 检查 MinIO 服务
kubectl -n argo get svc minio

# 测试 MinIO 连接
kubectl -n argo exec -it deployment/minio -- mc alias set local http://localhost:9000 admin password
```

### 5.2 日志查看

```bash
# 查看 Argo Server 日志
kubectl -n argo logs deployment/argo-server

# 查看工作流控制器日志
kubectl -n argo logs deployment/workflow-controller

# 查看特定步骤日志
kubectl -n argo logs <pod-name> -c main
kubectl -n argo logs <pod-name> -c wait  # 等待容器日志
```

### 5.3 清理资源

```bash
# 删除所有已完成的工作流
kubectl -n argo delete workflow --field-selector status.phase=Succeeded

# 删除所有失败的工作流
kubectl -n argo delete workflow --field-selector status.phase=Failed

# 删除所有工作流
kubectl -n argo delete workflow --all

# 清理 MinIO 中的旧 artifacts
kubectl -n argo exec -it deployment/minio -- mc rm --recursive --force local/dflow-artifacts/
```

---

## 6. 配置参考

### 6.1 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ARGO_SERVER` | Argo Server 地址 | `https://127.0.0.1:2746` |
| `MINIO_ENDPOINT` | MinIO 地址 | `minio:9000` |
| `MINIO_ACCESS_KEY` | MinIO 访问密钥 | `admin` |
| `MINIO_SECRET_KEY` | MinIO 密钥 | `admin123` |
| `MYSQL_HOST` | MySQL 主机 | `mysql` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户 | `root` |
| `MYSQL_PASSWORD` | MySQL 密码 | - |
| `MYSQL_DATABASE` | MySQL 数据库 | `financial_web_crawler` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | - |

### 6.2 dflow 配置

```python
from dflow import config, s3_config

# Argo 配置
config["host"] = "https://127.0.0.1:2746"
config["token"] = "your-token"  # 可选
config["mode"] = "default"  # 或 "debug"

# S3/MinIO 配置
s3_config["endpoint"] = "minio:9000"
s3_config["access_key"] = "admin"
s3_config["secret_key"] = "admin123"
s3_config["bucket"] = "dflow-artifacts"
s3_config["secure"] = False
```

---

## 7. 工作流对比

| 工作流 | 任务数 | 采集范围 | 预计耗时 | 使用场景 |
|--------|--------|----------|----------|----------|
| `full` | 41 | 所有组合 | ~30秒 | 首次采集、全量刷新 |
| `incremental` | 11 | today 数据 | ~10秒 | 5分钟定时刷新 |
| `quick` | 1 | 全部A股 today | ~3秒 | 1分钟快速刷新 |
| `stock` | 32 | 所有个股 | ~20秒 | 只需个股数据时 |

---

## 8. 与原有系统对比

| 功能 | APScheduler (原) | dflow (新) |
|------|------------------|------------|
| 调度方式 | 单机定时 | K8s CronWorkflow |
| 并行执行 | 串行 | 41 任务并行 |
| 失败恢复 | 手动 | 自动重试 |
| 监控 | 日志文件 | Argo UI |
| 扩展性 | 单机 | K8s 分布式 |
| 采集时间 | ~5分钟 | ~30秒 |

---

*dflow 操作指南 v1.0*
