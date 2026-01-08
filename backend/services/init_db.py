"""
数据库初始化模块
负责数据库连接、表结构创建和管理员账号初始化
"""

import contextlib
import logging
import time

import bcrypt
from core.config import ADMIN_CONFIG
from core.database import engine, get_db_session
from models.models import Base, User
from sqlalchemy import inspect, text

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


def check_database_connection() -> bool:
    """检查数据库连接是否可用"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def wait_for_database(max_retries: int = 30, delay: int = 2) -> None:
    """等待数据库服务可用"""
    logger.info("等待数据库服务就绪...")
    for attempt in range(1, max_retries + 1):
        if check_database_connection():
            logger.info("数据库连接成功")
            return
        logger.warning(f"数据库连接失败，第 {attempt}/{max_retries} 次重试...")
        if attempt < max_retries:
            time.sleep(delay)

    raise RuntimeError(
        f"无法连接到数据库，已重试 {max_retries} 次。请检查 MySQL 服务是否正常运行。"
    )


def apply_migrations() -> None:
    """应用数据库迁移，确保表结构是最新的"""
    try:
        inspector = inspect(engine)

        # 检查 user 表是否存在且缺少 username 列
        if "user" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("user")]
            if "username" not in columns:
                logger.info("检测到 user 表缺少 username 列，正在添加...")
                try:
                    with engine.begin() as conn:
                        conn.execute(text("ALTER TABLE user ADD COLUMN username VARCHAR(64) NULL"))
                        # 尝试创建索引
                        with contextlib.suppress(Exception):
                            conn.execute(text("CREATE INDEX ix_user_username ON user(username)"))
                    logger.info("成功添加 username 列到 user 表")
                except Exception as e:
                    logger.warning(f"执行数据库迁移时出错: {e}")
    except Exception as e:
        logger.warning(f"执行数据库迁移时出错: {e}")


def setup_admin_account() -> None:
    """创建或更新管理员账号"""
    admin_email = ADMIN_CONFIG.get("email")
    admin_password = ADMIN_CONFIG.get("password")
    admin_username = ADMIN_CONFIG.get("username", "admin")

    if not admin_email or not admin_password:
        logger.debug("未配置管理员账号环境变量，跳过管理员账号创建")
        return

    try:
        with get_db_session() as session:
            user = session.query(User).filter_by(email=admin_email).first()

            if not user:
                # 创建新管理员账号
                password_hash = _hash_password(admin_password)
                user = User(
                    email=admin_email,
                    username=admin_username,
                    password_hash=password_hash,
                    is_admin=1,
                    is_active=1,
                )
                session.add(user)
                logger.info(f"已创建管理员账号: {admin_email} (username: {admin_username})")
            else:
                # 更新现有用户
                updated = False
                if user.is_admin != 1:
                    user.is_admin = 1
                    updated = True
                if not user.username:
                    user.username = admin_username
                    updated = True
                if updated:
                    logger.info(f"已更新用户 {admin_email} 为管理员")
    except Exception as e:
        logger.error(f"设置管理员账号时出错: {e}")
        raise


def init_db(max_retries: int = 30, delay: int = 2) -> None:
    """
    初始化数据库

    执行完整的数据库初始化流程：
    1. 等待数据库服务可用
    2. 创建所有表结构
    3. 应用数据库迁移
    4. 创建管理员账号

    Args:
        max_retries: 最大重试次数，默认 30 次
        delay: 重试延迟（秒），默认 2 秒

    Raises:
        RuntimeError: 如果多次重试后仍无法连接数据库
    """
    logger.info("开始数据库初始化...")

    # 等待数据库服务可用
    wait_for_database(max_retries=max_retries, delay=delay)

    # 创建所有表结构
    logger.info("初始化数据库表结构...")
    Base.metadata.create_all(engine)
    logger.info("数据库表结构初始化完成")

    # 应用数据库迁移
    apply_migrations()

    # 创建管理员账号
    setup_admin_account()

    logger.info("数据库初始化完成")
