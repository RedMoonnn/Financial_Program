"""
缓存服务模块
处理Redis缓存操作
"""

import json
import logging
from typing import Optional

import redis
from core.config import CACHE_EXPIRE, REDIS_CONFIG

logger = logging.getLogger(__name__)

# Redis客户端
redis_client = redis.Redis(**REDIS_CONFIG)


class CacheService:
    """缓存服务类"""

    @staticmethod
    def cache_flow_data(
        code: str,
        flow_type: str,
        market_type: str,
        period: str,
        data: dict,
        expire: Optional[int] = None,
    ) -> None:
        """
        缓存资金流数据

        Args:
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期
            data: 数据字典
            expire: 过期时间（秒），默认使用配置值
        """
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        expire_seconds = expire or CACHE_EXPIRE["flow_data"]
        redis_client.setex(key, expire_seconds, json.dumps(data))
        logger.debug(f"资金流数据已缓存: {key}")

    @staticmethod
    def get_cached_flow_data(
        code: str, flow_type: str, market_type: str, period: str
    ) -> Optional[dict]:
        """
        获取缓存的资金流数据

        Args:
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期

        Returns:
            数据字典或None
        """
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"缓存数据JSON解析失败: {key}")
                return None
        return None

    @staticmethod
    def cache_image_url(
        code: str,
        flow_type: str,
        market_type: str,
        period: str,
        url: str,
        expire: Optional[int] = None,
    ) -> None:
        """
        缓存图片URL

        Args:
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期
            url: 图片URL
            expire: 过期时间（秒），默认使用配置值
        """
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        expire_seconds = expire or CACHE_EXPIRE["image_url"]
        redis_client.setex(key, expire_seconds, url)
        logger.debug(f"图片URL已缓存: {key}")

    @staticmethod
    def get_cached_image_url(
        code: str, flow_type: str, market_type: str, period: str
    ) -> Optional[str]:
        """
        获取缓存的图片URL

        Args:
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期

        Returns:
            图片URL或None
        """
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        return redis_client.get(key)


def set_data_ready(flag: bool) -> None:
    """
    设置数据就绪状态

    Args:
        flag: True表示数据就绪，False表示未就绪
    """
    expire_seconds = CACHE_EXPIRE["data_ready"]
    redis_client.setex("DATA_READY", expire_seconds, "1" if flag else "0")
    logger.info(f"数据就绪状态已更新: {flag}")


def get_data_ready() -> bool:
    """
    获取数据就绪状态

    Returns:
        True if data is ready, False otherwise
    """
    value = redis_client.get("DATA_READY")
    return value == "1"
