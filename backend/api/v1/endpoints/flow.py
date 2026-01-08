"""
资金流数据查询路由模块
"""

import logging

from core.config import DATABASE_CONFIG
from core.database import get_db_session_dependency
from fastapi import APIRouter, Depends, Query
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/flow", tags=["flow"])


@router.get("")
async def get_flow(
    flow_type: str = Query(..., description="资金流类型"),
    market_type: str = Query(..., description="市场类型"),
    period: str = Query(..., description="周期"),
    session: Session = Depends(get_db_session_dependency),
):
    """
    查询资金流数据

    - **flow_type**: 资金流类型（如 Stock_Flow, Sector_Flow）
    - **market_type**: 市场类型（如 All_Stocks, SH_A_Shares）
    - **period**: 周期（如 Today, 3_Day, 5_Day, 10_Day）
    注意：period格式需与爬虫创建的表名格式一致
    """
    table_name = f"{flow_type}_{market_type}_{period}".replace("-", "_")
    logger.info(f"查询表: {table_name}, 数据库: {DATABASE_CONFIG['database']}")

    try:
        # 检查表是否存在
        inspector = inspect(session.bind)
        if table_name not in inspector.get_table_names():
            logger.warning(f"表不存在: {table_name}")
            return {"data": [], "cached": False, "error": "未找到数据表"}

        # 使用参数化查询防止SQL注入
        # 注意：表名不能参数化，但我们已经验证了表名的格式
        query = text(f"SELECT * FROM `{table_name}` ORDER BY crawl_time DESC LIMIT 100")
        result = session.execute(query)
        rows = [dict(row._mapping) for row in result]

        logger.info(f"查询到 {len(rows)} 条数据")
        return {"data": rows, "cached": False}
    except Exception as e:
        logger.error(f"查询表异常: {e}", exc_info=True)
        return {"data": [], "cached": False, "error": str(e)}
