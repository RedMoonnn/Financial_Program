"""
服务层模块
提供统一的服务接口导出，保持向后兼容
"""

# 导入所有服务类（保持向后兼容）
from core.database import SessionLocal, get_db_session, get_db_session_dependency

from services.auth.email_service import EmailService
from services.auth.user_service import UserService
from services.common.cache_service import CacheService, get_data_ready, set_data_ready
from services.common.chat_service import ChatService
from services.common.task_service import TaskService
from services.flow.flow_data_service import FlowDataService
from services.flow.flow_image_service import FlowImageService
from services.init_db import init_db
from services.report.report_service import ReportService

# 导出所有服务类和函数
__all__ = [
    # 服务类
    "UserService",
    "EmailService",
    "TaskService",
    "FlowDataService",
    "FlowImageService",
    "ReportService",
    "ChatService",
    "CacheService",
    # 函数
    "init_db",
    "set_data_ready",
    "get_data_ready",
    # 数据库相关
    "SessionLocal",
    "get_db_session",
    "get_db_session_dependency",
]
