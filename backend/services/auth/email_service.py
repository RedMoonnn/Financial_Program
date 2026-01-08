"""
邮件服务模块
处理验证码发送和验证
"""

import logging
import random
import smtplib
import string
from email.header import Header
from email.mime.text import MIMEText

import redis
from core.config import (
    REDIS_CONFIG,
    SMTP_CONFIG,
    VERIFICATION_CODE_CONFIG,
    validate_smtp_config,
)

from services.exceptions import EmailServiceException

logger = logging.getLogger(__name__)

# Redis客户端
redis_client = redis.Redis(**REDIS_CONFIG)


class EmailService:
    """邮件服务类"""

    @staticmethod
    def send_code(email: str, code: str) -> None:
        """
        发送验证码邮件

        Args:
            email: 收件人邮箱
            code: 验证码

        Raises:
            EmailServiceException: 如果SMTP配置不完整或发送失败
        """
        # 验证配置
        is_valid, error_msg = validate_smtp_config()
        if not is_valid:
            raise EmailServiceException(error_msg)

        smtp_server = SMTP_CONFIG["server"]
        smtp_port = SMTP_CONFIG["port"]
        smtp_user = SMTP_CONFIG["user"]
        smtp_password = SMTP_CONFIG["password"]

        # 构建邮件内容
        content = (
            f"尊敬的用户：\n\n"
            f"您正在使用金融数据平台进行身份验证，本次验证码为：{code}。\n"
            f"验证码5分钟内有效，请勿泄露给他人。\n\n"
            f"如非本人操作，请忽略本邮件。\n\n"
            f"—— 金融分析小助手\n"
        )

        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = str(Header("金融分析小助手", "utf-8")) + f" <{smtp_user}>"
        msg["To"] = email
        msg["Subject"] = Header("智能金融数据采集分析平台验证码", "utf-8")

        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.set_debuglevel(0)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [email], msg.as_string())
            server.quit()
            logger.info(f"验证码邮件已发送: {email}")
        except smtplib.SMTPAuthenticationError as e:
            raise EmailServiceException(
                f"SMTP认证失败，请检查用户名和密码（授权码）是否正确: {e}"
            ) from e
        except smtplib.SMTPConnectError as e:
            raise EmailServiceException(
                f"无法连接到SMTP服务器 {smtp_server}:{smtp_port}，请检查服务器地址和端口: {e}"
            ) from e
        except smtplib.SMTPException as e:
            raise EmailServiceException(f"SMTP错误: {e}") from e
        except Exception as e:
            raise EmailServiceException(f"邮件发送失败: {e}") from e

    @staticmethod
    def gen_and_store_code(email: str) -> str:
        """
        生成并存储验证码

        Args:
            email: 用户邮箱

        Returns:
            生成的验证码
        """
        code_length = VERIFICATION_CODE_CONFIG["length"]
        code = "".join(random.choices(string.digits, k=code_length))
        expire_seconds = VERIFICATION_CODE_CONFIG["expire_seconds"]
        redis_client.setex(f"email:code:{email}", expire_seconds, code)
        logger.debug(f"验证码已生成并存储: {email}")
        return code

    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        """
        验证验证码

        Args:
            email: 用户邮箱
            code: 验证码

        Returns:
            True if code is valid, False otherwise
        """
        real_code = redis_client.get(f"email:code:{email}")
        is_valid = real_code == code
        if is_valid:
            logger.debug(f"验证码验证成功: {email}")
        else:
            logger.warning(f"验证码验证失败: {email}")
        return is_valid
