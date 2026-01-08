"""
配置管理模块
统一管理应用配置，避免硬编码
"""

import os
from typing import Optional

# Redis配置
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
    "password": os.getenv("REDIS_PASSWORD", ""),
    "decode_responses": True,
}

# SMTP配置
SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER"),
    "port": int(os.getenv("SMTP_PORT", 587)),
    "user": os.getenv("SMTP_USER"),
    "password": os.getenv("SMTP_PASSWORD"),
}

# 管理员配置
ADMIN_CONFIG = {
    "email": os.getenv("ADMIN_EMAIL"),
    "password": os.getenv("ADMIN_PASSWORD"),
    "username": os.getenv("ADMIN_USERNAME", "admin"),
}

# 验证码配置
VERIFICATION_CODE_CONFIG = {
    "length": 6,
    "expire_seconds": 300,  # 5分钟
    "charset": "digits",
}

# 缓存过期时间配置（秒）
CACHE_EXPIRE = {
    "flow_data": 3600,  # 1小时
    "image_url": 3600,  # 1小时
    "chat_history": 7 * 24 * 3600,  # 7天
    "data_ready": 24 * 3600,  # 24小时
}

# JWT配置
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET", "secret"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 60 * 24 * 7,  # 7天
}

# 数据库配置
DATABASE_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "test"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "charset": "utf8mb4",
}


def get_smtp_config() -> dict:
    """获取SMTP配置"""
    return SMTP_CONFIG.copy()


def validate_smtp_config() -> tuple[bool, Optional[str]]:
    """验证SMTP配置是否完整"""
    required_keys = ["server", "user", "password"]
    missing = [key for key in required_keys if not SMTP_CONFIG.get(key)]
    if missing:
        return False, f"SMTP配置不完整，缺少: {', '.join(missing)}"
    return True, None


def get_jwt_config() -> dict:
    """获取JWT配置"""
    return JWT_CONFIG.copy()


def get_database_config() -> dict:
    """获取数据库配置"""
    return DATABASE_CONFIG.copy()
