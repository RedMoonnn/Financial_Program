# 金融数据采集平台 dflow 重构指南（简易版）

## 1. 概述

### 为什么用 dflow

| 当前问题 | dflow 解决方案 |
|---------|---------------|
| 串行采集 32 个组合，约 5 分钟 | 并行执行，约 30 秒 |
| APScheduler 单机定时 | K8s CronWorkflow，高可用 |
| 失败需手动重启 | 自动重试 + 断点恢复 |
| 日志分散 | Argo UI 可视化监控 |

### 重构后架构

```
┌─────────────────────────────────────────────────────────┐
│                    dflow 工作流                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────── 并行采集层 (41个任务) ───────────────┐  │
│  │  个股: 8市场 × 4周期 = 32 任务                     │  │
│  │  板块: 3板块 × 3周期 = 9 任务                      │  │
│  └─────────────────────┬─────────────────────────────┘  │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────────┐│
│  │                 数据汇总存储 MySQL                   ││
│  └─────────────────────┬───────────────────────────────┘│
│                        ▼                                │
│  ┌─────────────────────────────────────────────────────┐│
│  │                 AI 分析 (Deepseek)                  ││
│  └─────────────────────┬───────────────────────────────┘│
│                        ▼                                │
│  ┌─────────────────────────────────────────────────────┐│
│  │                 生成报告 → MinIO                    ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 2. 环境准备

```bash
# 1. 安装 minikube + argo
minikube start --memory 4096 --cpus 4
kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/deepmodeling/dflow/master/manifests/quick-start-postgres.yaml

# 2. 端口转发
kubectl -n argo port-forward deployment/argo-server 2746:2746 --address 0.0.0.0 &
kubectl -n argo port-forward deployment/minio 9000:9000 --address 0.0.0.0 &

# 3. 安装 pydflow
pip install pydflow
```

---

## 3. OP 设计

### 3.1 需要创建的 OP

| OP 名称 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `CrawlStockFlowOP` | 采集个股资金流 | market_choice, day_choice | data_file, count |
| `CrawlSectorFlowOP` | 采集板块资金流 | detail_choice, day_choice | data_file, count |
| `StoreToMySQLOP` | 批量存储数据 | data_files[] | total_count |
| `AIAnalysisOP` | AI 智能分析 | query | analysis_result |
| `GenerateReportOP` | 生成报告 | analysis_result | report_url |

### 3.2 OP 实现示例

```python
from dflow.python import OP, OPIO, Artifact, Parameter
from pathlib import Path

class CrawlStockFlowOP(OP):
    """个股资金流采集 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIO({
            "market_choice": Parameter(int),   # 1-8
            "day_choice": Parameter(int),      # 1-4
        })

    @classmethod
    def get_output_sign(cls):
        return OPIO({
            "data_file": Artifact(Path),
            "count": Parameter(int),
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        # 复用现有 crawler.py 的采集逻辑
        from crawler.crawler import fetch_flow_data, market_names
        import json

        market_choice = op_in["market_choice"]
        day_choice = op_in["day_choice"]
        periods = ["today", "3d", "5d", "10d"]

        data = fetch_flow_data(
            flow_type="Stock_Flow",
            market_type=market_names[market_choice - 1],
            period=periods[day_choice - 1],
            pages=1,
            flow_choice=1,
            market_choice=market_choice,
            day_choice=day_choice,
        )

        output_path = Path(f"/tmp/stock_{market_choice}_{day_choice}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)

        return OPIO({
            "data_file": output_path,
            "count": len(data),
        })
```

---

## 4. 工作流实现

### 4.1 完整流水线

```python
from dflow import Workflow, Step, Slices
from dflow.python import PythonOPTemplate

def create_pipeline():
    wf = Workflow(name="financial-pipeline")

    # Step 1: 并行采集个股 (32 个任务)
    stock_template = PythonOPTemplate(
        CrawlStockFlowOP,
        image="python:3.9",
        python_packages=["requests", "pymysql"],
    )

    market_choices = []
    day_choices = []
    for m in range(1, 9):
        for d in range(1, 5):
            market_choices.append(m)
            day_choices.append(d)

    stock_step = Step(
        name="crawl-stock",
        template=stock_template,
        slices=Slices(
            input_parameter=["market_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "market_choice": market_choices,
            "day_choice": day_choices,
        },
    )
    wf.add(stock_step)

    # Step 2: 存储数据
    store_step = Step(
        name="store-data",
        template=PythonOPTemplate(StoreToMySQLOP, ...),
        artifacts={
            "data_files": stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_step)

    # Step 3: AI 分析
    ai_step = Step(
        name="ai-analysis",
        template=PythonOPTemplate(AIAnalysisOP, ...),
        parameters={"query": "分析今日市场资金流向"},
    )
    wf.add(ai_step)

    return wf

# 运行
wf = create_pipeline()
wf.submit()
print(f"提交成功: {wf.id}")
```

### 4.2 增量更新流水线

```python
def create_incremental():
    """只采集 today 数据，用于频繁刷新"""
    wf = Workflow(name="incremental-update")

    # 只采集 8 个市场的 today 数据
    step = Step(
        name="crawl-today",
        template=stock_template,
        slices=Slices(input_parameter=["market_choice"]),
        parameters={
            "market_choice": list(range(1, 9)),
            "day_choice": 1,  # today
        },
    )
    wf.add(step)
    return wf
```

---

## 5. 目录结构

```
backend/
├── dflow_pipeline/
│   ├── __init__.py
│   ├── config.py              # 配置
│   ├── run.py                 # 启动脚本
│   ├── ops/
│   │   ├── crawl_op.py        # 采集 OP
│   │   ├── store_op.py        # 存储 OP
│   │   └── ai_op.py           # AI 分析 OP
│   └── workflows/
│       ├── full_pipeline.py   # 完整流水线
│       └── incremental.py     # 增量更新
└── ...
```

---

## 6. 运行方式

```bash
# 运行完整流水线
python -m dflow_pipeline.run full

# 运行增量更新
python -m dflow_pipeline.run incremental

# 查看 Argo UI
open https://127.0.0.1:2746
```

---

## 7. 定时任务

使用 K8s CronWorkflow：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata:
  name: financial-cron
spec:
  schedule: "*/5 * * * *"  # 每 5 分钟
  workflowSpec:
    entrypoint: main
    templates:
      - name: main
        container:
          image: financial-crawler:latest
          command: ["python", "-m", "dflow_pipeline.run", "incremental"]
```

---

## 8. 关键收益

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 全量采集时间 | ~5 分钟 | ~30 秒 |
| 失败恢复 | 手动 | 自动 |
| 监控方式 | 查日志 | Argo UI |
| 扩展性 | 单机 | 分布式 |

---

## 9. 实施步骤

1. **安装环境**：minikube + argo + pydflow
2. **创建 OP**：将现有函数封装为 PythonOPTemplate
3. **组装工作流**：使用 Slices 实现并行
4. **测试运行**：先跑通简单版本
5. **部署定时任务**：配置 CronWorkflow
6. **迁移切换**：逐步替换 APScheduler

---

*简易版指南 v1.0*
