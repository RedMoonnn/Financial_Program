"""
Redis 缓存客户端模块
提供统一的 Redis 客户端实例（单例模式）
"""

from typing import Optional

import redis

from core.config import REDIS_CONFIG

# Redis 客户端单例
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    获取Redis客户端（单例模式）

    Returns:
        Redis客户端实例
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(**REDIS_CONFIG)
    return _redis_client


# 向后兼容：保留redis_client变量
redis_client = get_redis_client()
