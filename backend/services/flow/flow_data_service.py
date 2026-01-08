"""
资金流数据服务模块
处理资金流数据的存储和查询
"""

import logging
from typing import Any, Dict, List, Optional

from core.database import get_db_session
from models.models import FlowData
from utils.utils import get_now

from services.flow.flow_data_query import get_all_latest_flow_data

logger = logging.getLogger(__name__)


class FlowDataService:
    """资金流数据服务类"""

    @staticmethod
    def save_flow_data(data_list: List[Dict[str, Any]], task_id: int) -> None:
        """
        保存资金流数据列表

        Args:
            data_list: 资金流数据列表
            task_id: 关联的任务ID
        """
        with get_db_session() as session:
            for data in data_list:
                flow_data = FlowData(
                    code=data["code"],
                    name=data["name"],
                    flow_type=data["flow_type"],
                    market_type=data["market_type"],
                    period=data["period"],
                    latest_price=data.get("latest_price"),
                    change_percentage=data.get("change_percentage"),
                    main_flow_net_amount=data.get("main_flow_net_amount"),
                    main_flow_net_percentage=data.get("main_flow_net_percentage"),
                    extra_large_order_flow_net_amount=data.get("extra_large_order_flow_net_amount"),
                    extra_large_order_flow_net_percentage=data.get(
                        "extra_large_order_flow_net_percentage"
                    ),
                    large_order_flow_net_amount=data.get("large_order_flow_net_amount"),
                    large_order_flow_net_percentage=data.get("large_order_flow_net_percentage"),
                    medium_order_flow_net_amount=data.get("medium_order_flow_net_amount"),
                    medium_order_flow_net_percentage=data.get("medium_order_flow_net_percentage"),
                    small_order_flow_net_amount=data.get("small_order_flow_net_amount"),
                    small_order_flow_net_percentage=data.get("small_order_flow_net_percentage"),
                    crawl_time=get_now(),
                    task_id=task_id,
                )
                session.merge(flow_data)  # merge可避免唯一索引冲突

            logger.info(f"已保存 {len(data_list)} 条资金流数据，任务ID: {task_id}")

    @staticmethod
    def _flow_data_to_dict(flow_data: FlowData) -> Dict[str, Any]:
        """将FlowData对象转换为字典"""
        return {
            "code": flow_data.code,
            "name": flow_data.name,
            "flow_type": flow_data.flow_type,
            "market_type": flow_data.market_type,
            "period": flow_data.period,
            "latest_price": flow_data.latest_price,
            "change_percentage": flow_data.change_percentage,
            "main_flow_net_amount": flow_data.main_flow_net_amount,
            "main_flow_net_percentage": flow_data.main_flow_net_percentage,
            "extra_large_order_flow_net_amount": flow_data.extra_large_order_flow_net_amount,
            "extra_large_order_flow_net_percentage": flow_data.extra_large_order_flow_net_percentage,
            "large_order_flow_net_amount": flow_data.large_order_flow_net_amount,
            "large_order_flow_net_percentage": flow_data.large_order_flow_net_percentage,
            "medium_order_flow_net_amount": flow_data.medium_order_flow_net_amount,
            "medium_order_flow_net_percentage": flow_data.medium_order_flow_net_percentage,
            "small_order_flow_net_amount": flow_data.small_order_flow_net_amount,
            "small_order_flow_net_percentage": flow_data.small_order_flow_net_percentage,
            "crawl_time": str(flow_data.crawl_time),
        }

    @staticmethod
    def get_latest_flow_data(
        code: str, flow_type: str, market_type: str, period: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取最新的资金流数据

        Args:
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期

        Returns:
            资金流数据字典或None
        """
        with get_db_session() as session:
            result = (
                session.query(FlowData)
                .filter_by(code=code, flow_type=flow_type, market_type=market_type, period=period)
                .order_by(FlowData.crawl_time.desc())
                .first()
            )

            if result:
                return FlowDataService._flow_data_to_dict(result)
            return None

    @staticmethod
    def get_latest_flow_data_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取最新的资金流数据

        Args:
            name: 股票名称（支持模糊匹配）

        Returns:
            资金流数据字典或None
        """
        with get_db_session() as session:
            result = (
                session.query(FlowData)
                .filter(FlowData.name.like(f"%{name}%"))
                .order_by(FlowData.crawl_time.desc())
                .first()
            )

            if result:
                return FlowDataService._flow_data_to_dict(result)
            return None

    @staticmethod
    def get_all_latest_flow_data() -> List[Dict[str, Any]]:
        """
        获取所有最新的资金流数据

        Returns:
            资金流数据列表
        """
        return get_all_latest_flow_data()
