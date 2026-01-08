"""
任务服务模块
处理数据采集任务的管理
"""

import logging
from typing import Optional

from core.database import get_db_session
from models.models import FlowTask, TaskStatus
from utils.utils import get_now

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""

    @staticmethod
    def create_task(flow_type: str, market_type: str, period: str, pages: int) -> FlowTask:
        """
        创建新的采集任务

        Args:
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期
            pages: 页数

        Returns:
            FlowTask对象
        """
        with get_db_session() as session:
            task = FlowTask(
                flow_type=flow_type,
                market_type=market_type,
                period=period,
                pages=pages,
                status=TaskStatus.pending,
                start_time=get_now(),
            )
            session.add(task)
            session.refresh(task)
            logger.info(f"任务已创建: {task.id}")
            return task

    @staticmethod
    def update_task_status(
        task_id: int, status: TaskStatus, error_msg: Optional[str] = None
    ) -> None:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            error_msg: 错误信息（可选）
        """
        with get_db_session() as session:
            task = session.query(FlowTask).filter_by(id=task_id).first()
            if task:
                task.status = status
                task.end_time = get_now()
                if error_msg:
                    task.error_msg = error_msg
                logger.info(f"任务状态已更新: {task_id} -> {status.value}")
            else:
                logger.warning(f"任务不存在: {task_id}")
