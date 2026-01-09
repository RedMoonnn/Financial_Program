"""
用户服务模块
处理用户注册、登录、密码管理等业务逻辑
"""

import logging
from typing import Optional

import bcrypt
from core.database import get_db_session
from models.models import User

from services.exceptions import UserServiceException

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """
    对密码进行 bcrypt 哈希

    Args:
        password: 原始密码

    Returns:
        哈希后的密码字符串

    Note:
        bcrypt 限制密码不能超过 72 字节，如果超过会自动截断
    """
    # bcrypt 限制密码不能超过 72 字节
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        logger.warning(f"密码超过 72 字节限制（当前 {len(password_bytes)} 字节），将截断到 72 字节")
        password_bytes = password_bytes[:72]

    # 直接使用 bcrypt 库生成哈希，避免 passlib 初始化问题
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    # bcrypt.hashpw 返回 bytes，需要解码为字符串
    return password_hash.decode("utf-8")


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

            password_hash = _hash_password(password)
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
            # 使用 bcrypt 库验证密码
            password_bytes = password.encode("utf-8")
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            try:
                return bcrypt.checkpw(password_bytes, user.password_hash.encode("utf-8"))
            except Exception:
                return False

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
            user = session.query(User).filter_by(email=email).first()
            if user:
                # 在 Session 关闭前访问属性，确保它们被加载
                # 这样可以避免 DetachedInstanceError
                _ = user.is_admin
                _ = user.is_active
                _ = user.email
                _ = user.username
                # 将对象从 Session 中分离，但保留已加载的属性值
                session.expunge(user)
            return user

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

            user.password_hash = _hash_password(new_password)
            logger.info(f"用户密码已更新: {email}")
            return True

    @staticmethod
    def get_all_users() -> list[User]:
        """
        获取所有用户列表

        Returns:
            List of User objects
        """
        with get_db_session() as session:
            users = session.query(User).all()
            for user in users:
                # 访问属性以加载数据
                _ = user.is_admin
                _ = user.is_active
                session.expunge(user)
            return users

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            True if successful

        Raises:
            UserServiceException: 如果用户不存在
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise UserServiceException("用户不存在")

            # TODO: 考虑关联数据的处理，目前采用级联删除或置空
            # 如果配置了数据库外键级联删除，这里只需要删除用户
            session.delete(user)
            logger.info(f"用户已删除: ID {user_id}")
            return True

    @staticmethod
    def user_to_dict(user: User) -> dict:
        """
        将User对象转换为字典

        Args:
            user: User对象

        Returns:
            用户信息字典
        """
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": bool(user.is_admin == 1),
            "is_active": bool(user.is_active == 1),
            "created_at": str(user.created_at) if user.created_at else None,
        }
