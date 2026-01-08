"""
Redis 缓存客户端模块
提供统一的 Redis 客户端实例
"""

import redis

from core.config import REDIS_CONFIG

# 统一的 Redis 客户端实例
redis_client = redis.Redis(**REDIS_CONFIG)
