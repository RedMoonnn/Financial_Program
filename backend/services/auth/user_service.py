"""
用户服务模块
处理用户注册、登录、密码管理等业务逻辑
"""

import logging
from typing import Optional

from core.database import get_db_session
from models.models import User
from passlib.hash import bcrypt

from services.exceptions import UserServiceException

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""

    @staticmethod
    def register(email: str, password: str) -> bool:
        """
        注册新用户

        Args:
            email: 用户邮箱
            password: 用户密码

        Returns:
            True if successful

        Raises:
            UserServiceException: 如果邮箱已注册
        """
        with get_db_session() as session:
            if session.query(User).filter_by(email=email).first():
                raise UserServiceException("邮箱已注册")

            password_hash = bcrypt.hash(password)
            user = User(email=email, password_hash=password_hash)
            session.add(user)
            logger.info(f"用户注册成功: {email}")
            return True

    @staticmethod
    def verify_password(email: str, password: str) -> bool:
        """
        验证用户密码

        Args:
            email: 用户邮箱
            password: 用户密码

        Returns:
            True if password is correct, False otherwise
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                return False
            return bcrypt.verify(password, user.password_hash)

    @staticmethod
    def get_user(email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 用户邮箱

        Returns:
            User object or None
        """
        with get_db_session() as session:
            return session.query(User).filter_by(email=email).first()

    @staticmethod
    def set_password(email: str, new_password: str) -> bool:
        """
        设置用户新密码

        Args:
            email: 用户邮箱
            new_password: 新密码

        Returns:
            True if successful

        Raises:
            UserServiceException: 如果用户不存在
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                raise UserServiceException("用户不存在")

            user.password_hash = bcrypt.hash(new_password)
            logger.info(f"用户密码已更新: {email}")
            return True
