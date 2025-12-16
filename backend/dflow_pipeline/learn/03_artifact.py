#!/usr/bin/env python3
"""
dflow 学习教程 - 第3课：Artifact（文件传递）

学习如何在 Step 之间传递文件。这是爬虫项目的核心！

运行方式：
    cd /home/chy/dev/Financial_Program/backend
    PYTHONPATH=. python dflow_pipeline/learn/03_artifact.py
"""

import json
from pathlib import Path
from dflow import Workflow, Step
from dflow.python import OP, OPIO, OPIOSign, Artifact, PythonOPTemplate


# ============================================================
# Artifact vs Parameter
# ============================================================
"""
Parameter（参数）：
- 用于传递简单数据：str, int, float, bool
- 数据量小（通常 < 256KB）
- 直接存储在 Argo 的参数系统中

Artifact（工件/文件）：
- 用于传递文件或大数据
- 数据量可以很大
- 存储在 S3/MinIO 中
- 在你的爬虫项目中，采集的 JSON 数据就是 Artifact
"""


class WriteDataOP(OP):
    """
    第一个 OP：生成数据并写入文件
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "items": list,  # 要写入的数据列表
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "data_file": Artifact(Path),  # 输出一个文件！
                "count": int,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        items = op_in["items"]

        # 创建数据
        data = {
            "total": len(items),
            "items": items,
        }

        # 写入文件
        output_path = Path("/tmp/data.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[WriteDataOP] 写入了 {len(items)} 条数据到 {output_path}")

        return OPIO(
            {
                "data_file": output_path,  # 返回文件路径
                "count": len(items),
            }
        )


class ReadDataOP(OP):
    """
    第二个 OP：读取文件并处理
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "data_file": Artifact(Path),  # 接收一个文件！
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "summary": str,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        data_file = op_in["data_file"]

        # 读取文件
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 处理数据
        total = data["total"]
        items = data["items"]
        summary = f"读取到 {total} 条数据: {', '.join(items)}"

        print(f"[ReadDataOP] {summary}")

        return OPIO({"summary": summary})


# ============================================================
# 创建工作流
# ============================================================


def create_workflow():
    wf = Workflow(name="artifact-tutorial")

    write_template = PythonOPTemplate(WriteDataOP, image="python:3.9-slim")
    read_template = PythonOPTemplate(ReadDataOP, image="python:3.9-slim")

    # Step 1: 写入数据
    step1 = Step(
        name="write-data",
        template=write_template,
        parameters={
            "items": ["苹果", "香蕉", "橙子"],  # 模拟爬取的数据
        },
    )
    wf.add(step1)

    # Step 2: 读取数据
    # 关键：使用 artifacts 参数传递文件，而不是 parameters
    step2 = Step(
        name="read-data",
        template=read_template,
        artifacts={
            "data_file": step1.outputs.artifacts["data_file"],  # 引用上一步的文件！
        },
    )
    wf.add(step2)

    return wf


# ============================================================
# 图示说明
# ============================================================
"""
执行流程：

    ┌─────────────────────┐
    │     WriteDataOP     │
    │  items: [苹果,香蕉,橙子]
    │                     │
    │  → 写入 data.json   │
    │  → 上传到 MinIO     │ (K8s 模式)
    └──────────┬──────────┘
               │
               │ data_file (文件 Artifact)
               │
               ▼
    ┌─────────────────────┐
    │     ReadDataOP      │
    │  ← 从 MinIO 下载    │ (K8s 模式)
    │  ← 读取 data.json   │
    │                     │
    │  → "读取到 3 条数据" │
    └─────────────────────┘

在 K8s 模式下：
1. WriteDataOP 的 Pod 执行完后，文件会上传到 MinIO
2. ReadDataOP 的 Pod 启动时，会从 MinIO 下载文件
3. 这样两个 Pod 之间就能传递任意大小的文件

这就是你的爬虫项目的工作原理！
- CrawlOP 生成 JSON 文件 → 上传到 MinIO
- StoreOP 从 MinIO 下载 → 存入 MySQL
"""


if __name__ == "__main__":
    from dflow import config

    config["mode"] = "debug"

    print("=" * 60)
    print("dflow 学习教程 - 第3课：Artifact（文件传递）")
    print("=" * 60)
    print()
    print("流程: WriteDataOP → data.json → ReadDataOP")
    print()

    wf = create_workflow()

    print("执行工作流...")
    print("-" * 40)
    wf.submit()
    print("-" * 40)
    print()
    print("完成！文件在两个 Step 之间成功传递。")
    print()
    print("提示：在 K8s 模式下，文件会通过 MinIO 传递。")
