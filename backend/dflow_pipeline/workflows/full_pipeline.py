"""
完整流水线 - 并行采集所有数据并存储
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


def create_full_pipeline(name: str = "financial-full-pipeline") -> Workflow:
    """
    创建完整的数据采集流水线

    流程：
    1. 并行采集 32 个个股资金流组合 (8 市场 × 4 周期)
    2. 并行采集 9 个板块资金流组合 (3 板块 × 3 周期)
    3. 并行存储所有数据到 MySQL
    """
    wf = Workflow(name=name)

    # 获取 backend 目录路径（用于本地调试时设置 PYTHONPATH）
    from pathlib import Path
    backend_dir = str(Path(__file__).parent.parent.parent.absolute())

    # ========== Step 1: 并行采集个股资金流 (32 个任务) ==========
    stock_template = PythonOPTemplate(
        CrawlStockFlowOP,
        image="python:3.9-slim",
        envs={"PYTHONPATH": backend_dir},
    )

    # 生成参数组合: 8 市场 × 4 周期 = 32
    stock_market_choices = []
    stock_day_choices = []
    for m in range(1, 9):
        for d in range(1, 5):
            stock_market_choices.append(m)
            stock_day_choices.append(d)

    stock_step = Step(
        name="crawl-stock",
        template=stock_template,
        slices=Slices(
            "{{item}}",
            input_parameter=["market_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "market_choice": stock_market_choices,
            "day_choice": stock_day_choices,
        },
    )
    wf.add(stock_step)

    # ========== Step 2: 并行采集板块资金流 (9 个任务) ==========
    sector_template = PythonOPTemplate(
        CrawlSectorFlowOP,
        image="python:3.9-slim",
        envs={"PYTHONPATH": backend_dir},
    )

    # 生成参数组合: 3 板块 × 3 周期 = 9
    sector_detail_choices = []
    sector_day_choices = []
    for detail in range(1, 4):
        for d in range(1, 4):
            sector_detail_choices.append(detail)
            sector_day_choices.append(d)

    sector_step = Step(
        name="crawl-sector",
        template=sector_template,
        slices=Slices(
            "{{item}}",
            input_parameter=["detail_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "detail_choice": sector_detail_choices,
            "day_choice": sector_day_choices,
        },
    )
    wf.add(sector_step)

    # ========== Step 3: 并行存储个股数据到 MySQL ==========
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

    # ========== Step 4: 并行存储板块数据到 MySQL ==========
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


def create_stock_only_pipeline(name: str = "financial-stock-pipeline") -> Workflow:
    """
    只采集个股资金流的流水线
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

    stock_market_choices = []
    stock_day_choices = []
    for m in range(1, 9):
        for d in range(1, 5):
            stock_market_choices.append(m)
            stock_day_choices.append(d)

    stock_step = Step(
        name="crawl-stock",
        template=stock_template,
        slices=Slices(
            "{{item}}",
            input_parameter=["market_choice", "day_choice"],
            output_artifact=["data_file"],
        ),
        parameters={
            "market_choice": stock_market_choices,
            "day_choice": stock_day_choices,
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
        slices=Slices(
            "{{item}}",
            input_artifact=["data_file"],
        ),
        artifacts={
            "data_file": stock_step.outputs.artifacts["data_file"],
        },
    )
    wf.add(store_step)

    return wf


if __name__ == "__main__":
    # 本地测试
    wf = create_full_pipeline()
    print(f"Workflow created: {wf.name}")
    print(f"Steps: {[s.name for s in wf.steps]}")
