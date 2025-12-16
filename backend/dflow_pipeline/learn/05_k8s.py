#!/usr/bin/env python3
"""
dflow 学习教程 - 第5课：提交到 K8s（真正的分布式执行）

前面都是 debug 模式（本地执行），现在学习提交到 K8s 集群。

运行方式：
    cd /home/chy/dev/Financial_Program/backend

    # Debug 模式（本地）
    PYTHONPATH=. python dflow_pipeline/learn/05_k8s.py --debug

    # K8s 模式（提交到 Argo）
    PYTHONPATH=. python dflow_pipeline/learn/05_k8s.py
"""

import sys
from dflow import Workflow, Step
from dflow.python import OP, OPIO, OPIOSign, PythonOPTemplate


class SimpleOP(OP):
    """简单的 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({"message": str})

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({"result": str})

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        message = op_in["message"]
        result = f"[在 K8s Pod 中执行] {message}"
        print(result)
        return OPIO({"result": result})


def create_workflow():
    wf = Workflow(name="k8s-tutorial")

    template = PythonOPTemplate(
        SimpleOP,
        image="python:3.9-slim",  # K8s 会拉取这个镜像创建 Pod
    )

    step = Step(
        name="simple-step",
        template=template,
        parameters={"message": "Hello from K8s!"},
    )
    wf.add(step)

    return wf


# ============================================================
# Debug 模式 vs K8s 模式
# ============================================================
"""
Debug 模式（本地）：
┌─────────────────────────────────────────┐
│  你的电脑                                │
│                                         │
│  python script.py                       │
│       │                                 │
│       ▼                                 │
│  ┌─────────────┐                       │
│  │   dflow    │ → 直接在本地进程执行    │
│  │  (debug)   │                        │
│  └─────────────┘                       │
└─────────────────────────────────────────┘

K8s 模式（分布式）：
┌─────────────────────────────────────────┐
│  你的电脑                                │
│                                         │
│  python script.py                       │
│       │                                 │
│       ▼                                 │
│  ┌─────────────┐    提交任务            │
│  │   dflow    │ ─────────────────────┐ │
│  └─────────────┘                     │ │
└──────────────────────────────────────│─┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────┐
│  K8s 集群 (Minikube)                                    │
│                                                         │
│  ┌──────────────┐                                      │
│  │ Argo Server  │ ← 接收工作流定义                      │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼ 创建 Pod                                      │
│  ┌──────────────┐      ┌──────────────┐               │
│  │  Pod         │      │    MinIO     │               │
│  │ python:3.9   │ ←──→ │  (存储文件)  │               │
│  │ 执行你的代码  │      │              │               │
│  └──────────────┘      └──────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘

为什么要用 K8s 模式？
1. 并行执行：32 个 Pod 同时运行，比顺序执行快 32 倍
2. 资源隔离：每个任务在独立容器中，互不影响
3. 容错：Pod 失败可以自动重试
4. 监控：Argo UI 可以看到每个任务的状态
"""


if __name__ == "__main__":
    # 导入配置
    from dflow_pipeline import config as _  # noqa: F401

    # 检查是否是 debug 模式
    debug_mode = "--debug" in sys.argv

    if debug_mode:
        from dflow import config

        config["mode"] = "debug"
        print("=" * 60)
        print("运行模式: DEBUG（本地执行）")
        print("=" * 60)
    else:
        print("=" * 60)
        print("运行模式: K8S（提交到 Argo）")
        print("=" * 60)
        print()
        print("前提条件：")
        print("  1. minikube 正在运行")
        print("  2. 端口转发已启动：")
        print("     kubectl -n argo port-forward svc/argo-server 2746:2746 &")
        print("     kubectl -n argo port-forward svc/minio 9000:9000 &")
        print()

    wf = create_workflow()

    print(f"工作流名称: {wf.name}")
    print()
    print("提交工作流...")
    print("-" * 40)

    wf.submit()

    print("-" * 40)
    print()
    print(f"工作流 ID: {wf.id}")

    if not debug_mode:
        print()
        print("查看状态：")
        print(f"  kubectl -n argo get workflow {wf.id}")
        print()
        print("查看日志：")
        print(
            f"  kubectl -n argo logs -l workflows.argoproj.io/workflow={wf.id} -c main"
        )
        print()
        print("Argo UI：")
        print(f"  https://127.0.0.1:2746/workflows/argo/{wf.id}")
