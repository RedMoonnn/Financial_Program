#!/usr/bin/env python3
"""
dflow 工作流启动脚本

使用方法：
    python -m dflow_pipeline.run full          # 运行完整流水线（采集+分析+存储）
    python -m dflow_pipeline.run crawl         # 只运行采集+存储（不分析）
    python -m dflow_pipeline.run incremental   # 运行增量更新
    python -m dflow_pipeline.run quick         # 运行快速刷新
    python -m dflow_pipeline.run debug         # 本地调试模式
    python -m dflow_pipeline.run hello         # Hello World 测试
    python -m dflow_pipeline.run simple        # 简化版爬虫测试
"""

import sys
import argparse


def setup_debug_mode():
    """设置调试模式 - 必须在导入 workflows 之前调用"""
    # 先导入 config 模块以设置 debug_workdir
    from . import config as pipeline_config  # noqa: F401
    from dflow import config as dflow_config

    dflow_config["mode"] = "debug"


def run_workflow(workflow, debug=False):
    """运行工作流"""
    print(f"Submitting workflow: {workflow.name}")
    workflow.submit()
    print("Workflow submitted successfully!")
    print(f"Workflow ID: {workflow.id}")

    if not debug:
        print(f"View in Argo UI: https://127.0.0.1:2746/workflows/argo/{workflow.id}")


def main():
    parser = argparse.ArgumentParser(description="dflow Financial Pipeline Runner")
    parser.add_argument(
        "command",
        choices=["full", "crawl", "incremental", "quick", "debug", "hello", "simple"],
        help="Pipeline to run: full(采集+分析+存储), crawl(只采集+存储), incremental, quick, debug, hello, simple",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in local debug mode (no K8s required)",
    )

    args = parser.parse_args()

    # 如果是调试模式，必须在导入 workflows 之前设置
    is_debug = args.debug or args.command == "debug"
    if is_debug:
        setup_debug_mode()
        print("Running in DEBUG mode (local execution, no K8s required)")

    # 延迟导入 workflows（在设置 debug 模式之后）
    from .workflows.full_pipeline import (
        create_full_pipeline,
        create_crawl_only_pipeline,
    )
    from .workflows.incremental import (
        create_incremental_pipeline,
        create_quick_refresh_pipeline,
    )

    if args.command == "full":
        # 完整流水线：采集 -> 数据库存储 + AI 分析 -> MinIO 存储
        print("启动完整流水线: 数据采集 + 数据库存储 + DeepSeek 分析 + MinIO 报告存储")
        wf = create_full_pipeline()
        run_workflow(wf, debug=is_debug)

    elif args.command == "crawl":
        # 只采集和存储，不进行 AI 分析
        print("启动采集流水线: 数据采集 + 数据库存储（无 AI 分析）")
        wf = create_crawl_only_pipeline()
        run_workflow(wf, debug=is_debug)

    elif args.command == "incremental":
        wf = create_incremental_pipeline()
        run_workflow(wf, debug=is_debug)

    elif args.command == "quick":
        wf = create_quick_refresh_pipeline()
        run_workflow(wf, debug=is_debug)

    elif args.command == "debug":
        # 本地调试模式运行增量更新
        wf = create_incremental_pipeline()
        run_workflow(wf, debug=True)

    elif args.command == "hello":
        # 最简单的 Hello World 工作流（用于学习）
        from .workflows.simple_test import create_hello_workflow

        wf = create_hello_workflow()
        run_workflow(wf, debug=is_debug)

    elif args.command == "simple":
        # 简化版爬虫工作流（单任务，不用 Slices）
        from .workflows.simple_test import create_crawl_workflow

        wf = create_crawl_workflow()
        run_workflow(wf, debug=is_debug)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
