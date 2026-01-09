"""
资金流数据查询路由模块
统一使用flow_data_query模块的查询函数
"""

import logging

from core.config import DATABASE_CONFIG
from fastapi import APIRouter, Query
from services.flow.flow_data_query import query_table_data

from api.middleware import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/flow", tags=["flow"])


@router.get("")
async def get_flow(
    flow_type: str = Query(..., description="资金流类型"),
    market_type: str = Query(..., description="市场类型"),
    period: str = Query(..., description="周期"),
    limit: int = Query(100, description="查询条数限制", ge=1, le=1000),
):
    """
    查询资金流数据

    - **flow_type**: 资金流类型（如 Stock_Flow, Sector_Flow）
    - **market_type**: 市场类型（如 All_Stocks, SH_A_Shares）
    - **period**: 周期（如 Today, 3_Day, 5_Day, 10_Day）
    - **limit**: 查询条数限制，默认100，最大1000
    注意：period格式需与爬虫创建的表名格式一致
    """
    try:
        table_name = f"{flow_type}_{market_type}_{period}".replace("-", "_")

        # 安全获取数据库名称
        db_name = "unknown"
        if isinstance(DATABASE_CONFIG, dict):
            db_name = DATABASE_CONFIG.get("database", "unknown")

        logger.info(f"查询表: {table_name}, 数据库: {db_name}")

        # 统一使用flow_data_query模块的查询函数
        flow_data = query_table_data(table_name, limit=limit)

        if not flow_data:
            logger.warning(f"表 {table_name} 不存在或无数据")
            return APIResponse.error(
                message="未找到数据表", code=404, data={"data": [], "cached": False}
            )

        # 转换数据格式：flow_data_query返回的是结构化格式，需要转换为原始格式
        # 返回原始表结构的数据
        rows = []
        for item in flow_data:
            row = item["data"].copy()
            row["flow_type"] = item["flow_type"]
            row["market_type"] = item["market_type"]
            row["period"] = item["period"]
            rows.append(row)

        logger.info(f"查询到 {len(rows)} 条数据")
        return APIResponse.success(data={"data": rows, "cached": False}, message="查询成功")
    except Exception as e:
        logger.error(f"查询表异常: {e}", exc_info=True)
        return APIResponse.error(message=str(e), code=500, data={"data": [], "cached": False})
