"""
聊天服务模块
处理聊天历史记录的存储和查询
"""

import json
import logging
from typing import Any, Dict, List

from core.cache import redis_client
from core.config import CACHE_EXPIRE

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""

    @staticmethod
    def save_history(user_id: int, history: List[Dict[str, Any]]) -> None:
        """
        保存聊天历史

        Args:
            user_id: 用户ID
            history: 聊天历史记录列表
        """
        key = f"chat:history:{user_id}"
        expire_seconds = CACHE_EXPIRE["chat_history"]
        redis_client.setex(key, expire_seconds, json.dumps(history))
        logger.debug(f"聊天历史已保存: 用户ID {user_id}")

    @staticmethod
    def get_history(user_id: int) -> List[Dict[str, Any]]:
        """
        获取聊天历史

        Args:
            user_id: 用户ID

        Returns:
            聊天历史记录列表
        """
        key = f"chat:history:{user_id}"
        data = redis_client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.error(f"聊天历史JSON解析失败: 用户ID {user_id}")
                return []
        return []

    @staticmethod
    def clear_history(user_id: int) -> None:
        """
        清除聊天历史

        Args:
            user_id: 用户ID
        """
        key = f"chat:history:{user_id}"
        redis_client.delete(key)
        logger.info(f"聊天历史已清除: 用户ID {user_id}")
