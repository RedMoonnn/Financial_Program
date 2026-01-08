"""
配置管理模块
使用 pydantic-settings 进行类型安全的配置管理
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """Redis 配置"""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="localhost", description="Redis 主机")
    port: int = Field(default=6379, description="Redis 端口")
    db: int = Field(default=0, description="Redis 数据库编号")
    password: str = Field(default="", description="Redis 密码")

    @property
    def config_dict(self) -> dict:
        """转换为字典格式（用于 redis.Redis）"""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
            "decode_responses": True,
        }


class SMTPSettings(BaseSettings):
    """SMTP 配置"""

    model_config = SettingsConfigDict(env_prefix="SMTP_")

    server: Optional[str] = Field(default=None, description="SMTP 服务器")
    port: int = Field(default=587, description="SMTP 端口")
    user: Optional[str] = Field(default=None, description="SMTP 用户名")
    password: Optional[str] = Field(default=None, description="SMTP 密码")

    def is_configured(self) -> bool:
        """检查 SMTP 配置是否完整"""
        return bool(self.server and self.user and self.password)

    def validate(self) -> tuple[bool, Optional[str]]:
        """验证 SMTP 配置是否完整"""
        if not self.is_configured():
            missing = []
            if not self.server:
                missing.append("server")
            if not self.user:
                missing.append("user")
            if not self.password:
                missing.append("password")
            return False, f"SMTP配置不完整，缺少: {', '.join(missing)}"
        return True, None

    @property
    def config_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "server": self.server,
            "port": self.port,
            "user": self.user,
            "password": self.password,
        }


class AdminSettings(BaseSettings):
    """管理员配置"""

    model_config = SettingsConfigDict(env_prefix="ADMIN_")

    email: Optional[str] = Field(default=None, description="管理员邮箱")
    password: Optional[str] = Field(default=None, description="管理员密码")
    username: str = Field(default="admin", description="管理员用户名")

    @property
    def config_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "email": self.email,
            "password": self.password,
            "username": self.username,
        }


class JWTSettings(BaseSettings):
    """JWT 配置"""

    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str = Field(default="secret", description="JWT 密钥")
    algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7, description="访问令牌过期时间（分钟）"
    )

    @property
    def config_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
        }


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    model_config = SettingsConfigDict(env_prefix="MYSQL_")

    host: str = Field(default="localhost", description="MySQL 主机")
    port: int = Field(default=3306, description="MySQL 端口")
    user: str = Field(default="root", description="MySQL 用户名")
    password: str = Field(default="", description="MySQL 密码")
    database: str = Field(default="test", description="MySQL 数据库名")
    charset: str = Field(default="utf8mb4", description="字符集")

    @property
    def config_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset,
        }


class AppSettings(BaseSettings):
    """应用配置"""

    # 验证码配置
    verification_code_length: int = Field(default=6, description="验证码长度")
    verification_code_expire_seconds: int = Field(default=300, description="验证码过期时间（秒）")
    verification_code_charset: str = Field(default="digits", description="验证码字符集")

    # 缓存过期时间配置（秒）
    cache_expire_flow_data: int = Field(default=3600, description="资金流数据缓存过期时间")
    cache_expire_image_url: int = Field(default=3600, description="图片URL缓存过期时间")
    cache_expire_chat_history: int = Field(
        default=7 * 24 * 3600, description="聊天历史缓存过期时间"
    )
    cache_expire_data_ready: int = Field(default=24 * 3600, description="数据就绪状态缓存过期时间")

    @property
    def verification_code_config(self) -> dict:
        """验证码配置字典"""
        return {
            "length": self.verification_code_length,
            "expire_seconds": self.verification_code_expire_seconds,
            "charset": self.verification_code_charset,
        }

    @property
    def cache_expire(self) -> dict:
        """缓存过期时间配置字典"""
        return {
            "flow_data": self.cache_expire_flow_data,
            "image_url": self.cache_expire_image_url,
            "chat_history": self.cache_expire_chat_history,
            "data_ready": self.cache_expire_data_ready,
        }


# 创建配置实例
redis_settings = RedisSettings()
smtp_settings = SMTPSettings()
admin_settings = AdminSettings()
jwt_settings = JWTSettings()
database_settings = DatabaseSettings()
app_settings = AppSettings()

# 向后兼容的配置字典（保持原有接口）
REDIS_CONFIG = redis_settings.config_dict
SMTP_CONFIG = smtp_settings.config_dict
ADMIN_CONFIG = admin_settings.config_dict
JWT_CONFIG = jwt_settings.config_dict
DATABASE_CONFIG = database_settings.config_dict
VERIFICATION_CODE_CONFIG = app_settings.verification_code_config
CACHE_EXPIRE = app_settings.cache_expire


def validate_smtp_config() -> tuple[bool, Optional[str]]:
    """验证SMTP配置是否完整（向后兼容函数）"""
    return smtp_settings.validate()
