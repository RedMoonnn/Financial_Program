"""
增量更新流水线 - 只采集 today 数据，用于频繁刷新
"""
from dflow import Workflow, Step
from dflow.python import PythonOPTemplate, Slices

from ..ops.crawl_op import CrawlStockFlowOP, CrawlSectorFlowOP
from ..ops.store_op import StoreSingleFileOP


def get_db_envs():
    """获取数据库环境变量配置"""
    import os
    return {
        "MYSQL_HOST": os.getenv("MYSQL_HOST", "mysql"),
        "MYSQL_PORT": os.getenv("MYSQL_PORT", "3306"),
        "MYSQL_USER": os.getenv("MYSQL_USER", "root"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
    }


def create_incremental_pipeline(name: str = "financial-incremental") -> Workflow:
    """
    创建增量更新流水线 - 只采集 today 数据

    流程：
    1. 并行采集 8 个市场的 today 数据
    2. 并行采集 3 个板块的 today 数据
    3. 并行存储所有数据到 MySQL
    """
    wf = Workflow(name=name)

    # 获取 backend 目录路径（用于本地调试时设置 PYTHONPATH）
    import os
    from pathlib import Path
    backend_dir = str(Path(__file__).parent.parent.parent.absolute())

    # ========== Step 1: 并行采集个股 today 数据 (8 个任务) ==========
    stock_template = PythonOPTemplate(
        CrawlStockFlowOP,
        image="python:3.9-slim",
        envs={"PYTHONPATH": backend_dir},
    )

    stock_step = Step(
        name="crawl-stock-today",
        template=stock_template,
        slices=Slices(
            "{{item}}",
            input_parameter=["market_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "market_choice": list(range(1, 9)),  # 1-8
            "day_choice": [1] * 8,  # 全部为 today
        },
    )
    wf.add(stock_step)

    # ========== Step 2: 并行采集板块 today 数据 (3 个任务) ==========
    sector_template = PythonOPTemplate(
        CrawlSectorFlowOP,
        image="python:3.9-slim",
        envs={"PYTHONPATH": backend_dir},
    )

    sector_step = Step(
        name="crawl-sector-today",
        template=sector_template,
        slices=Slices(
            "{{item}}",
            input_parameter=["detail_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "detail_choice": list(range(1, 4)),  # 1-3
            "day_choice": [1] * 3,  # 全部为 today
        },
    )
    wf.add(sector_step)

    # ========== Step 3: 并行存储数据 ==========
    db_envs = get_db_envs()
    db_envs["PYTHONPATH"] = backend_dir
    store_template = PythonOPTemplate(
        StoreSingleFileOP,
        image="python:3.9-slim",
        envs=db_envs,
    )

    store_stock_step = Step(
        name="store-stock",
        template=store_template,
        slices=Slices(
            "{{item}}",
            input_artifact=["data_file"],
        ),
        artifacts={
            "data_file": stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_stock_step)

    store_sector_step = Step(
        name="store-sector",
        template=store_template,
        slices=Slices(
            "{{item}}",
            input_artifact=["data_file"],
        ),
        artifacts={
            "data_file": sector_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_sector_step)

    return wf


def create_quick_refresh_pipeline(name: str = "financial-quick-refresh") -> Workflow:
    """
    快速刷新流水线 - 只采集全部A股的 today 数据

    适用于每分钟级别的快速刷新
    """
    wf = Workflow(name=name)

    # 获取 backend 目录路径
    from pathlib import Path
    backend_dir = str(Path(__file__).parent.parent.parent.absolute())

    stock_template = PythonOPTemplate(
        CrawlStockFlowOP,
        image="python:3.9-slim",
        envs={"PYTHONPATH": backend_dir},
    )

    # 只采集 All_Stocks (market_choice=1) 的 today (day_choice=1) 数据
    stock_step = Step(
        name="crawl-all-stocks-today",
        template=stock_template,
        parameters={
            "market_choice": 1,
            "day_choice": 1,
        },
    )
    wf.add(stock_step)

    db_envs = get_db_envs()
    db_envs["PYTHONPATH"] = backend_dir
    store_template = PythonOPTemplate(
        StoreSingleFileOP,
        image="python:3.9-slim",
        envs=db_envs,
    )

    store_step = Step(
        name="store-data",
        template=store_template,
        artifacts={
            "data_file": stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_step)

    return wf


if __name__ == "__main__":
    # 本地测试
    wf = create_incremental_pipeline()
    print(f"Workflow created: {wf.name}")
    print(f"Steps: {[s.name for s in wf.steps]}")
