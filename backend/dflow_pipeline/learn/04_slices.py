#!/usr/bin/env python3
"""
dflow 学习教程 - 第4课：Slices（并行切片）

学习如何让一个 Step 并行执行多次。这是你爬虫项目的核心技术！

运行方式：
    cd /home/chy/dev/Financial_Program/backend
    PYTHONPATH=. python dflow_pipeline/learn/04_slices.py
"""

import json
from pathlib import Path
from typing import List
from dflow import Workflow, Step
from dflow.python import OP, OPIO, OPIOSign, Artifact, PythonOPTemplate, Slices


# ============================================================
# 什么是 Slices？
# ============================================================
"""
问题：你有 8 个市场 × 4 个周期 = 32 种组合要采集
方案1：写 32 个 Step（太蠢了）
方案2：用 Slices，一个 Step 自动切成 32 个并行任务！

Slices 的工作原理：
1. 你给一个参数列表，比如 market=[1,2,3,4], period=[1,2,3,4]
2. dflow 自动创建 4 个并行 Pod
3. 每个 Pod 接收一组参数：(1,1), (2,2), (3,3), (4,4)
4. 执行完后，输出会自动聚合

注意：参数是"同步切片"的，即第一个 Pod 拿 market[0] 和 period[0]
"""


class CrawlOP(OP):
    """
    模拟爬虫 OP：根据 market 和 period 采集数据
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "market": int,  # 市场编号
                "period": int,  # 周期编号
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "data_file": Artifact(Path),  # 输出文件
                "count": int,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        market = op_in["market"]
        period = op_in["period"]

        # 模拟采集数据
        data = {
            "market": market,
            "period": period,
            "stocks": [
                {"code": f"00000{i}", "price": 10.0 + market + period}
                for i in range(3)  # 模拟 3 条数据
            ],
        }

        # 写入文件
        output_path = Path(f"/tmp/data_m{market}_p{period}.json")
        with open(output_path, "w") as f:
            json.dump(data, f)

        print(f"[CrawlOP] 市场={market}, 周期={period}, 采集了 3 条数据")

        return OPIO(
            {
                "data_file": output_path,
                "count": 3,
            }
        )


class AggregateOP(OP):
    """
    聚合 OP：汇总所有文件
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "data_files": Artifact(List[Path]),  # 接收多个文件！
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "total": int,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        data_files = op_in["data_files"]

        total = 0
        for f in data_files:
            with open(f) as fp:
                data = json.load(fp)
                total += len(data["stocks"])
                print(f"[AggregateOP] 读取 {f.name}: {len(data['stocks'])} 条")

        print(f"[AggregateOP] 总计: {total} 条数据")

        return OPIO({"total": total})


# ============================================================
# 创建工作流
# ============================================================


def create_workflow():
    wf = Workflow(name="slices-tutorial")

    crawl_template = PythonOPTemplate(CrawlOP, image="python:3.9-slim")
    agg_template = PythonOPTemplate(AggregateOP, image="python:3.9-slim")

    # Step 1: 并行采集（使用 Slices）
    # 注意：market 和 period 是同步切片的
    # market=[1,2,3,4] + period=[10,20,30,40]
    # → Pod0: market=1, period=10
    # → Pod1: market=2, period=20
    # → Pod2: market=3, period=30
    # → Pod3: market=4, period=40
    step1 = Step(
        name="crawl",
        template=crawl_template,
        slices=Slices(
            "{{item}}",  # 切片模式
            input_parameter=["market", "period"],  # 哪些参数要切片
            output_artifact=["data_file"],  # 哪些输出要聚合
        ),
        parameters={
            "market": [1, 2, 3, 4],  # 4 个市场
            "period": [10, 20, 30, 40],  # 4 个周期（同步！）
        },
    )
    wf.add(step1)

    # Step 2: 聚合所有文件
    # 关键：step1 的输出被聚合成了一个列表
    step2 = Step(
        name="aggregate",
        template=agg_template,
        artifacts={
            "data_files": step1.outputs.artifacts["data_file"],  # 这是一个列表！
        },
    )
    wf.add(step2)

    return wf


# ============================================================
# 图示说明
# ============================================================
"""
执行流程（4 个并行 Pod）：

                    ┌─────────────────┐
                    │    Workflow     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐
    │ CrawlOP │        │ CrawlOP │        │ CrawlOP │        │ CrawlOP │
    │ m=1,p=10│        │ m=2,p=20│        │ m=3,p=30│        │ m=4,p=40│
    │  Pod 0  │        │  Pod 1  │        │  Pod 2  │        │  Pod 3  │
    └────┬────┘        └────┬────┘        └────┬────┘        └────┬────┘
         │                  │                  │                  │
         │ file_0           │ file_1           │ file_2           │ file_3
         │                  │                  │                  │
         └──────────────────┼──────────────────┼──────────────────┘
                            │
                            ▼ 聚合成列表 [file_0, file_1, file_2, file_3]
                    ┌───────────────┐
                    │  AggregateOP  │
                    │ 读取所有文件  │
                    └───────────────┘

你的爬虫项目：
- 8 个市场 × 4 个周期 = 32 个并行 Pod
- 每个 Pod 采集一个组合的数据
- 然后存储 OP 并行处理 32 个文件
"""


if __name__ == "__main__":
    from dflow import config

    config["mode"] = "debug"

    print("=" * 60)
    print("dflow 学习教程 - 第4课：Slices（并行切片）")
    print("=" * 60)
    print()
    print("4 个参数组合并行执行：")
    print("  (market=1, period=10)")
    print("  (market=2, period=20)")
    print("  (market=3, period=30)")
    print("  (market=4, period=40)")
    print()

    wf = create_workflow()

    print("执行工作流...")
    print("-" * 40)
    wf.submit()
    print("-" * 40)
    print()
    print("完成！4 个 Pod 并行执行，结果自动聚合。")


"""
混合方案最佳：用 Slices 做粗粒度并行（分批），每个 Pod 内部用
  asyncio/多线程做细粒度并行。这样既利用了分布式扩展能力，又减少了 Pod
  数量和启动开销。
"""
