"""
数据库初始化模块
处理数据库表的创建和管理员账号的初始化
"""

import logging
import time

from core.config import ADMIN_CONFIG
from core.database import engine, get_db_session
from models.models import Base, User
from passlib.hash import bcrypt
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


def init_db(max_retries: int = 30, delay: int = 2) -> None:
    """
    初始化数据库

    创建所有表，并自动创建管理员账号（如果配置了环境变量）

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Raises:
        Exception: 如果多次重试后仍无法连接数据库
    """
    for i in range(max_retries):
        try:
            Base.metadata.create_all(engine)
            logger.info("数据库连接成功！")

            # 自动创建管理员账号
            _create_admin_user()

            return
        except OperationalError as e:
            logger.warning(f"数据库连接失败，第{i + 1}次重试，错误信息：{e}")
            time.sleep(delay)

    raise Exception("多次重试后仍无法连接数据库，请检查 MySQL 服务！")


def _create_admin_user() -> None:
    """创建管理员账号（如果配置了环境变量）"""
    admin_email = ADMIN_CONFIG["email"]
    admin_password = ADMIN_CONFIG["password"]
    admin_username = ADMIN_CONFIG["username"]

    if not admin_email or not admin_password:
        logger.debug("未配置管理员账号环境变量，跳过管理员账号创建")
        return

    with get_db_session() as session:
        user = session.query(User).filter_by(email=admin_email).first()

        if not user:
            # 创建新管理员账号
            password_hash = bcrypt.hash(admin_password)
            user = User(
                email=admin_email, username=admin_username, password_hash=password_hash, is_admin=1
            )
            session.add(user)
            logger.info(f"已自动创建管理员账号: {admin_email} (username: {admin_username})")
        else:
            # 确保现有用户的管理员标志正确
            if user.is_admin != 1:
                user.is_admin = 1
                if not user.username:
                    user.username = admin_username
                logger.info(f"已更新用户 {admin_email} 为管理员")
