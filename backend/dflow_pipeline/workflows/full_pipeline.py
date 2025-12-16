"""
完整流水线 - 优化版
使用 2 个 slice 并行采集数据，然后分两路：
1. 存储到数据库
2. 使用 DeepSeek 分析并将报告存储到 MinIO
"""

import os
from dflow import Workflow, Step
from dflow.python import PythonOPTemplate

# 导入 config 模块会自动加载 .env 文件
from .. import config as _  # noqa: F401

from ..ops.batch_crawl_op import BatchCrawlStockFlowOP, BatchCrawlSectorFlowOP
from ..ops.batch_store_op import BatchStoreToMySQLOP
from ..ops.deepseek_analysis_op import DeepSeekAnalysisOP
from ..ops.minio_store_op import StoreReportToMinIOOP


def get_db_envs():
    """获取数据库环境变量配置（从 .env 加载）"""
    return {
        "MYSQL_HOST": os.getenv("MYSQL_HOST", "mysql"),
        "MYSQL_PORT": os.getenv("MYSQL_PORT", "3306"),
        "MYSQL_USER": os.getenv("MYSQL_USER", "root"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD", "chen350627"),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
    }


def get_ai_envs():
    """获取 AI 相关环境变量配置（从 .env 加载）"""
    return {
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
        "DEEPSEEK_BASE_URL": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    }


def get_minio_envs():
    """获取 MinIO 环境变量配置（从 .env 加载）"""
    return {
        "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT", "minio:9000"),
        "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY", "admin"),
        "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY", "admin123"),
        "MINIO_SECURE": os.getenv("MINIO_SECURE", "False"),
        # 使用 MINIO_BUCKET 或 MINIO_REPORT_BUCKET
        "MINIO_REPORT_BUCKET": os.getenv(
            "MINIO_REPORT_BUCKET", os.getenv("MINIO_BUCKET", "data-financial-agent")
        ),
    }


def create_full_pipeline(name: str = "financial-full-pipeline") -> Workflow:
    """
    创建完整的数据采集+分析流水线（优化版）

    流程架构：
    ┌─────────────────────────────────────────────────────┐
    │                 Step 1: 并行采集                      │
    │  ┌──────────────────┐    ┌──────────────────┐       │
    │  │ crawl-stock      │    │ crawl-sector     │       │
    │  │ (批量采集个股)    │    │ (批量采集板块)    │       │
    │  └────────┬─────────┘    └────────┬─────────┘       │
    └───────────┼───────────────────────┼─────────────────┘
                │                       │
                ▼                       ▼
    ┌─────────────────────────────────────────────────────┐
    │              Step 2: 并行处理（分两路）                │
    │                                                      │
    │  路线 A: 数据库存储                                   │
    │  ┌──────────────────┐    ┌──────────────────┐       │
    │  │ store-stock      │    │ store-sector     │       │
    │  │ (存储个股数据)    │    │ (存储板块数据)    │       │
    │  └──────────────────┘    └──────────────────┘       │
    │                                                      │
    │  路线 B: AI 分析                                      │
    │  ┌──────────────────┐                               │
    │  │ ai-analysis      │──▶ DeepSeek 分析               │
    │  └────────┬─────────┘                               │
    │           │                                          │
    │           ▼                                          │
    │  ┌──────────────────┐                               │
    │  │ store-to-minio   │──▶ 报告存储到 MinIO            │
    │  └──────────────────┘                               │
    └─────────────────────────────────────────────────────┘

    优化点：
    - 只用 2 个 slice（个股+板块），而非 32+9 个
    - 数据库存储和 AI 分析并行执行
    - 分析报告自动存储到 MinIO
    """
    wf = Workflow(name=name)

    # 获取 dflow_pipeline 目录路径
    from pathlib import Path

    backend_dir = Path(__file__).parent.parent.parent.absolute()
    dflow_pipeline_dir = backend_dir / "dflow_pipeline"

    # pip 安装命令前缀（避免 root 用户警告）
    pip_prefix = "import subprocess; subprocess.run(['pip', 'install', '-q', '--root-user-action=ignore'"

    # ========== Step 1: 并行采集个股和板块数据 (2 个任务) ==========

    # 个股采集模板
    stock_crawl_template = PythonOPTemplate(
        BatchCrawlStockFlowOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'requests'])\n",
    )

    # 板块采集模板
    sector_crawl_template = PythonOPTemplate(
        BatchCrawlSectorFlowOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'requests'])\n",
    )

    # 添加采集步骤（并行执行）
    crawl_stock_step = Step(
        name="crawl-stock",
        template=stock_crawl_template,
    )
    wf.add(crawl_stock_step)

    crawl_sector_step = Step(
        name="crawl-sector",
        template=sector_crawl_template,
    )
    wf.add(crawl_sector_step)

    # ========== Step 2A: 数据库存储 ==========

    store_template = PythonOPTemplate(
        BatchStoreToMySQLOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        # MySQL 8.0 使用 caching_sha2_password 认证，需要 cryptography 包
        pre_script=f"{pip_prefix}, 'pymysql', 'cryptography'])\n",
        envs=get_db_envs(),
    )

    # 存储个股数据
    store_stock_step = Step(
        name="store-stock",
        template=store_template,
        artifacts={
            "data_file": crawl_stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_stock_step)

    # 存储板块数据
    store_sector_step = Step(
        name="store-sector",
        template=store_template,
        artifacts={
            "data_file": crawl_sector_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_sector_step)

    # ========== Step 2B: AI 分析 ==========

    analysis_template = PythonOPTemplate(
        DeepSeekAnalysisOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'openai'])\n",
        envs=get_ai_envs(),
    )

    ai_analysis_step = Step(
        name="ai-analysis",
        template=analysis_template,
        artifacts={
            "stock_data_file": crawl_stock_step.outputs.artifacts["data_file"],
            "sector_data_file": crawl_sector_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(ai_analysis_step)

    # ========== Step 3: 存储报告到 MinIO ==========

    minio_template = PythonOPTemplate(
        StoreReportToMinIOOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'minio'])\n",
        envs=get_minio_envs(),
    )

    store_report_step = Step(
        name="store-to-minio",
        template=minio_template,
        artifacts={
            "report_file": ai_analysis_step.outputs.artifacts["report_file"],
        },
    )
    wf.add(store_report_step)

    return wf


def create_crawl_only_pipeline(name: str = "financial-crawl-only") -> Workflow:
    """
    只采集数据（不分析），用于测试采集功能
    """
    wf = Workflow(name=name)

    from pathlib import Path

    backend_dir = Path(__file__).parent.parent.parent.absolute()
    dflow_pipeline_dir = backend_dir / "dflow_pipeline"

    pip_prefix = "import subprocess; subprocess.run(['pip', 'install', '-q', '--root-user-action=ignore'"

    # 个股采集
    stock_crawl_template = PythonOPTemplate(
        BatchCrawlStockFlowOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'requests'])\n",
    )

    crawl_stock_step = Step(
        name="crawl-stock",
        template=stock_crawl_template,
    )
    wf.add(crawl_stock_step)

    # 板块采集
    sector_crawl_template = PythonOPTemplate(
        BatchCrawlSectorFlowOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        pre_script=f"{pip_prefix}, 'requests'])\n",
    )

    crawl_sector_step = Step(
        name="crawl-sector",
        template=sector_crawl_template,
    )
    wf.add(crawl_sector_step)

    # 存储到数据库
    store_template = PythonOPTemplate(
        BatchStoreToMySQLOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],
        # MySQL 8.0 使用 caching_sha2_password 认证，需要 cryptography 包
        pre_script=f"{pip_prefix}, 'pymysql', 'cryptography'])\n",
        envs=get_db_envs(),
    )

    store_stock_step = Step(
        name="store-stock",
        template=store_template,
        artifacts={
            "data_file": crawl_stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_stock_step)

    store_sector_step = Step(
        name="store-sector",
        template=store_template,
        artifacts={
            "data_file": crawl_sector_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_sector_step)

    return wf


if __name__ == "__main__":
    # 本地测试
    wf = create_full_pipeline()
    print(f"Workflow created: {wf.name}")

    wf2 = create_crawl_only_pipeline()
    print(f"Crawl-only workflow created: {wf2.name}")
