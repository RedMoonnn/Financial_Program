#!/usr/bin/env python3
"""
dflow 工作流启动脚本

使用方法：
    python -m dflow_pipeline.run full          # 运行完整流水线
    python -m dflow_pipeline.run incremental   # 运行增量更新
    python -m dflow_pipeline.run quick         # 运行快速刷新
    python -m dflow_pipeline.run debug         # 本地调试模式
"""
import sys
import argparse

# 导入配置（初始化 dflow 配置）
from . import config  # noqa: F401

from .workflows.full_pipeline import create_full_pipeline, create_stock_only_pipeline
from .workflows.incremental import create_incremental_pipeline, create_quick_refresh_pipeline


def run_workflow(workflow, debug=False):
    """运行工作流"""
    if debug:
        # 本地调试模式
        from dflow import config as dflow_config
        dflow_config["mode"] = "debug"

    print(f"Submitting workflow: {workflow.name}")
    workflow.submit()
    print(f"Workflow submitted successfully!")
    print(f"Workflow ID: {workflow.id}")

    if not debug:
        print(f"View in Argo UI: https://127.0.0.1:2746/workflows/argo/{workflow.id}")


def main():
    parser = argparse.ArgumentParser(description="dflow Financial Pipeline Runner")
    parser.add_argument(
        "command",
        choices=["full", "incremental", "quick", "stock", "debug"],
        help="Pipeline to run",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in local debug mode",
    )

    args = parser.parse_args()

    if args.command == "full":
        wf = create_full_pipeline()
        run_workflow(wf, debug=args.debug)

    elif args.command == "incremental":
        wf = create_incremental_pipeline()
        run_workflow(wf, debug=args.debug)

    elif args.command == "quick":
        wf = create_quick_refresh_pipeline()
        run_workflow(wf, debug=args.debug)

    elif args.command == "stock":
        wf = create_stock_only_pipeline()
        run_workflow(wf, debug=args.debug)

    elif args.command == "debug":
        # 本地调试模式运行增量更新
        wf = create_incremental_pipeline()
        run_workflow(wf, debug=True)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
