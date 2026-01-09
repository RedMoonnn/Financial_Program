"""
报告服务模块
处理报告的管理
"""

import logging
from typing import List, Optional

from core.database import get_db_session
from models.models import Report, User

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
        with get_db_session(auto_commit=False) as session:
            reports = (
                session.query(Report)
                .filter_by(user_id=user_id)
                .order_by(Report.created_at.desc())
                .all()
            )
            return reports

    @staticmethod
    def list_all_reports() -> List[Report]:
        """
        获取所有用户的报告列表（管理员使用）

        Returns:
            所有报告列表
        """
        with get_db_session(auto_commit=False) as session:
            reports = session.query(Report).order_by(Report.created_at.desc()).all()
            return reports

    @staticmethod
    def get_report_by_filename(file_name: str) -> Optional[Report]:
        """
        根据文件名获取报告

        Args:
            file_name: 文件名

        Returns:
            报告对象，如果不存在则返回None
        """
        with get_db_session(auto_commit=False) as session:
            report = session.query(Report).filter_by(file_name=file_name).first()
            return report

    @staticmethod
    def delete_report(file_name: str, user_id: int, is_admin: bool = False) -> bool:
        """
        删除报告（需要验证权限）

        Args:
            file_name: 文件名
            user_id: 当前用户ID
            is_admin: 是否为管理员

        Returns:
            True if successful, False if not found or no permission

        Raises:
            PermissionError: 如果用户没有权限删除该报告
        """
        report = ReportService.get_report_by_filename(file_name)
        if not report:
            return False

        # 管理员可以删除任何报告，普通用户只能删除自己的报告
        if not is_admin and report.user_id != user_id:
            raise PermissionError("无权删除该报告")

        with get_db_session() as session:
            session.delete(report)
            logger.info(f"报告已删除: {file_name} (用户ID: {user_id}, 管理员: {is_admin})")
            return True

    @staticmethod
    def get_user_info_map(user_ids: set[int]) -> dict[int, dict]:
        """
        获取用户信息映射（用于管理员查看报告所有者）

        Args:
            user_ids: 用户ID集合

        Returns:
            用户信息字典，key为用户ID，value为用户信息字典
        """
        if not user_ids:
            return {}

        with get_db_session() as session:
            users = session.query(User).filter(User.id.in_(user_ids)).all()
            return {u.id: {"id": u.id, "email": u.email, "username": u.username} for u in users}

    @staticmethod
    def report_to_dict(report: Report, include_user: bool = False, user_map: dict = None) -> dict:
        """
        将Report对象转换为字典

        Args:
            report: Report对象
            include_user: 是否包含用户信息（管理员模式）
            user_map: 用户信息映射字典

        Returns:
            报告信息字典
        """
        result = {
            "id": report.id,
            "type": report.report_type,
            "file_url": report.file_url,
            "file_name": report.file_name,
            "created_at": str(report.created_at) if report.created_at else None,
        }
        if include_user and user_map:
            owner = user_map.get(report.user_id, {})
            result["user_id"] = report.user_id
            result["user_email"] = owner.get("email", "未知")
            result["username"] = owner.get("username")
        return result
