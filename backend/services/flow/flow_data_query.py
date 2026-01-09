"""
资金流数据查询模块
使用SQLAlchemy统一管理数据库连接
"""

import logging
from typing import Any, Dict, List

from core.database import get_db_session
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


def _row_to_dict(row: tuple) -> Dict[str, Any]:
    """将查询结果行转换为字典格式"""
    return {
        "type": "stock" if row[2] == "Stock_Flow" else "sector",
        "flow_type": row[2],
        "market_type": row[3],
        "period": row[4],
        "data": {
            "code": row[0],
            "name": row[1],
            "latest_price": row[5],
            "change_percentage": row[6],
            "main_flow_net_amount": row[7],
            "main_flow_net_percentage": row[8],
            "extra_large_order_flow_net_amount": row[9],
            "extra_large_order_flow_net_percentage": row[10],
            "large_order_flow_net_amount": row[11],
            "large_order_flow_net_percentage": row[12],
            "medium_order_flow_net_amount": row[13],
            "medium_order_flow_net_percentage": row[14],
            "small_order_flow_net_amount": row[15],
            "small_order_flow_net_percentage": row[16],
            "crawl_time": str(row[17]),
        },
    }


def get_all_latest_flow_data() -> List[Dict[str, Any]]:
    """
    遍历所有Stock_Flow_%和Sector_Flow_%分表，合并所有数据，返回结构化列表。
    """
    results = []
    with get_db_session() as session:
        # 使用SQLAlchemy inspector获取表名
        inspector_obj = inspect(session.bind)
        all_table_names = inspector_obj.get_table_names()

        # 筛选出Stock_Flow和Sector_Flow相关的表
        stock_tables = [t for t in all_table_names if t.startswith("Stock_Flow_")]
        sector_tables = [t for t in all_table_names if t.startswith("Sector_Flow_")]
        all_tables = stock_tables + sector_tables

        for table in all_tables:
            try:
                # 使用text()执行原生SQL查询
                query = text(
                    f"SELECT code, name, flow_type, market_type, period, latest_price, "
                    f"change_percentage, main_flow_net_amount, main_flow_net_percentage, "
                    f"extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, "
                    f"large_order_flow_net_amount, large_order_flow_net_percentage, "
                    f"medium_order_flow_net_amount, medium_order_flow_net_percentage, "
                    f"small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time "
                    f"FROM `{table}` ORDER BY crawl_time DESC"
                )
                result = session.execute(query)
                rows = result.fetchall()

                for row in rows:
                    results.append(_row_to_dict(row))
            except Exception as e:
                logger.error(f"查询表 {table} 出错: {e}", exc_info=True)

    return results


def query_table_data(table_name: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    查询指定表名的最新N条数据，返回结构化列表。

    Args:
        table_name: 表名
        limit: 查询条数限制，默认50

    Returns:
        资金流数据列表
    """
    results = []
    with get_db_session() as session:
        try:
            # 检查表是否存在
            inspector_obj = inspect(session.bind)
            if table_name not in inspector_obj.get_table_names():
                logger.warning(f"表不存在: {table_name}")
                return []

            # 使用text()执行原生SQL查询
            query = text(
                f"SELECT code, name, flow_type, market_type, period, latest_price, "
                f"change_percentage, main_flow_net_amount, main_flow_net_percentage, "
                f"extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, "
                f"large_order_flow_net_amount, large_order_flow_net_percentage, "
                f"medium_order_flow_net_amount, medium_order_flow_net_percentage, "
                f"small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time "
                f"FROM `{table_name}` ORDER BY crawl_time DESC LIMIT :limit"
            )
            result = session.execute(query, {"limit": limit})
            rows = result.fetchall()

            for row in rows:
                results.append(_row_to_dict(row))
        except Exception as e:
            logger.error(f"查询表 {table_name} 出错: {e}", exc_info=True)

    return results


def query_stock_flow_data(stock_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    遍历所有Stock_Flow_%和Sector_Flow_%分表，查找包含该股票名的最新N条数据。

    Args:
        stock_name: 股票名称（支持模糊匹配）
        limit: 查询条数限制，默认100

    Returns:
        资金流数据列表，按时间降序排列
    """
    results = []
    with get_db_session() as session:
        # 使用SQLAlchemy inspector获取表名
        inspector_obj = inspect(session.bind)
        all_table_names = inspector_obj.get_table_names()

        # 筛选出Stock_Flow和Sector_Flow相关的表
        stock_tables = [t for t in all_table_names if t.startswith("Stock_Flow_")]
        sector_tables = [t for t in all_table_names if t.startswith("Sector_Flow_")]
        all_tables = stock_tables + sector_tables

        for table in all_tables:
            try:
                # 使用text()执行原生SQL查询，使用参数化查询防止SQL注入
                query = text(
                    f"SELECT code, name, flow_type, market_type, period, latest_price, "
                    f"change_percentage, main_flow_net_amount, main_flow_net_percentage, "
                    f"extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, "
                    f"large_order_flow_net_amount, large_order_flow_net_percentage, "
                    f"medium_order_flow_net_amount, medium_order_flow_net_percentage, "
                    f"small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time "
                    f"FROM `{table}` WHERE name LIKE :pattern ORDER BY crawl_time DESC LIMIT :limit"
                )
                result = session.execute(query, {"pattern": f"%{stock_name}%", "limit": limit})
                rows = result.fetchall()

                for row in rows:
                    results.append(_row_to_dict(row))
            except Exception as e:
                logger.error(f"查询表 {table} 出错: {e}", exc_info=True)

    # 按时间降序排序，最多返回limit条
    results = sorted(results, key=lambda x: x["data"]["crawl_time"], reverse=True)
    return results[:limit]


if __name__ == "__main__":
    table_name = input("请输入要分析的表名（如Sector_Flow_Concept_Flow_10_Day）：").strip()
    if table_name:
        table_data = query_table_data(table_name, limit=50)
        print(f"表{table_name}最新50条数据：{table_data[:2]} ... 共{len(table_data)}条")
        if table_data:
            try:
                from services.ai.deepseek import DeepseekAgent

                # 只传递核心字段，防止token溢出
                slim_data = [
                    {
                        "type": d["type"],
                        "flow_type": d["flow_type"],
                        "market_type": d["market_type"],
                        "period": d["period"],
                        "data": {
                            "code": d["data"]["code"],
                            "name": d["data"]["name"],
                            "main_flow_net_amount": d["data"]["main_flow_net_amount"],
                            "main_flow_net_percentage": d["data"]["main_flow_net_percentage"],
                            "change_percentage": d["data"]["change_percentage"],
                            "crawl_time": d["data"]["crawl_time"],
                        },
                    }
                    for d in table_data
                ]
                user_message = f"请帮我分析一下表 {table_name} 的资金流情况"
                result = DeepseekAgent.analyze(slim_data, user_message=user_message, style="专业")
                print("\n=== Deepseek分析结果 ===\n")
                print(result)
            except Exception as e:
                print(f"调用Deepseek分析出错: {e}")
        else:
            print(f"表{table_name}无数据！")
