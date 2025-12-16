# dflow 学习教程

按顺序学习这些教程，从零开始理解 dflow。

## 教程列表

### 第1课：Hello World
```bash
PYTHONPATH=. python dflow_pipeline/learn/01_hello.py
```
学习内容：
- OP 的基本结构（input_sign, output_sign, execute）
- Workflow、Template、Step 的关系
- Debug 模式运行

### 第2课：Step 链式调用
```bash
PYTHONPATH=. python dflow_pipeline/learn/02_chain.py
```
学习内容：
- 多个 Step 顺序执行
- Step 之间传递参数（Parameters）
- `step.outputs.parameters["xxx"]` 引用上一步输出

### 第3课：Artifact（文件传递）
```bash
PYTHONPATH=. python dflow_pipeline/learn/03_artifact.py
```
学习内容：
- Artifact vs Parameter 的区别
- 如何在 Step 之间传递文件
- `Artifact(Path)` 类型定义

### 第4课：Slices（并行切片）⭐ 重点
```bash
PYTHONPATH=. python dflow_pipeline/learn/04_slices.py
```
学习内容：
- 如何让一个 Step 并行执行多次
- 参数同步切片的概念
- 输出自动聚合

### 第5课：提交到 K8s
```bash
# Debug 模式（本地）
PYTHONPATH=. python dflow_pipeline/learn/05_k8s.py --debug

# K8s 模式（提交到 Argo）
PYTHONPATH=. python dflow_pipeline/learn/05_k8s.py
```
学习内容：
- Debug 模式 vs K8s 模式的区别
- 如何查看工作流状态和日志
- 真正的分布式执行

---

## 核心概念总结

```
┌─────────────────────────────────────────────────────────────┐
│                        dflow 架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                           │
│  │    OP       │  操作（Operation）                         │
│  │             │  - 定义输入/输出签名                        │
│  │ input_sign  │  - 实现 execute() 方法                     │
│  │ output_sign │  - 类似于一个函数                          │
│  │ execute()   │                                           │
│  └──────┬──────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │  Template   │  模板                                      │
│  │             │  - 包装 OP 为 K8s 可执行单元               │
│  │ image       │  - 指定 Docker 镜像                        │
│  │ packages    │  - 指定依赖                                │
│  └──────┬──────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │    Step     │  步骤                                      │
│  │             │  - 关联 Template 和参数                     │
│  │ template    │  - 可以使用 Slices 并行                    │
│  │ parameters  │  - 可以引用其他 Step 的输出                │
│  │ artifacts   │                                           │
│  │ slices      │                                           │
│  └──────┬──────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │  Workflow   │  工作流                                    │
│  │             │  - 包含多个 Step                           │
│  │ add(step)   │  - 提交到 Argo 执行                        │
│  │ submit()    │                                           │
│  └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 你的爬虫项目结构

```
dflow_pipeline/
├── ops/
│   ├── crawl_op.py      # CrawlStockFlowOP, CrawlSectorFlowOP
│   └── store_op.py      # StoreSingleFileOP
│
├── workflows/
│   ├── full_pipeline.py # 完整流水线 (32+9 并行任务)
│   └── simple_test.py   # 简化版（学习用）
│
└── run.py               # 启动脚本
```

执行流程：
```
CrawlStockFlowOP (32 个并行 Pod)
       │
       ▼ 32 个 JSON 文件 (通过 MinIO)
       │
StoreSingleFileOP (32 个并行 Pod)
       │
       ▼
    MySQL
```
