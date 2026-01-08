"""
报告服务模块
处理报告的管理
"""

import logging
from typing import List

from core.database import get_db_session
from models.models import Report

logger = logging.getLogger(__name__)


class ReportService:
    """报告服务类"""

    @staticmethod
    def add_report(user_id: int, report_type: str, file_url: str, file_name: str) -> bool:
        """
        添加报告

        Args:
            user_id: 用户ID
            report_type: 报告类型
            file_url: 文件URL
            file_name: 文件名

        Returns:
            True if successful
        """
        with get_db_session() as session:
            report = Report(
                user_id=user_id,
                report_type=report_type,
                file_url=file_url,
                file_name=file_name,
            )
            session.add(report)
            logger.info(f"报告已添加: {file_name} (用户ID: {user_id})")
            return True

    @staticmethod
    def list_reports(user_id: int) -> List[Report]:
        """
        获取用户的报告列表

        Args:
            user_id: 用户ID

        Returns:
            报告列表
        """
        with get_db_session() as session:
            reports = (
                session.query(Report)
                .filter_by(user_id=user_id)
                .order_by(Report.created_at.desc())
                .all()
            )
            return reports
