"""
数据库连接和会话管理模块
提供统一的数据库会话管理，避免资源泄漏
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import database_settings

logger = logging.getLogger(__name__)


# 创建数据库引擎
def create_db_engine():
    """创建数据库引擎"""
    db_config = database_settings.config_dict
    db_url = (
        f"mysql+pymysql://{db_config['user']}:"
        f"{db_config['password']}@"
        f"{db_config['host']}:"
        f"{db_config['port']}/"
        f"{db_config['database']}?charset={db_config['charset']}"
    )
    return create_engine(db_url, echo=False, pool_pre_ping=True)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器

    使用示例:
        with get_db_session() as session:
            user = session.query(User).first()
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session_dependency():
    """
    用于FastAPI依赖注入的数据库会话生成器
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
