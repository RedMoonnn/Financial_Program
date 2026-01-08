"""
邮件服务模块
处理验证码发送和验证
"""

import logging
import random
import smtplib
import string
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from core.cache import redis_client
from core.config import (
    SMTP_CONFIG,
    VERIFICATION_CODE_CONFIG,
    validate_smtp_config,
)

from services.exceptions import EmailServiceException

logger = logging.getLogger(__name__)


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

        # 构建邮件内容 (MIMEMultipart alternative allows both text and html)
        msg = MIMEMultipart("alternative")

        # Plain text version
        text_content = (
            f"尊敬的用户：\n\n"
            f"您正在使用金融数据平台进行身份验证，本次验证码为：{code}。\n"
            f"验证码5分钟内有效，请勿泄露给他人。\n\n"
            f"如非本人操作，请忽略本邮件。\n\n"
            f"—— 金融分析小助手\n"
        )

        # HTML version

        # HTML version
        html_content = EmailService.get_email_template(code)

        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")

        msg.attach(part1)
        msg.attach(part2)

        # 使用 formataddr 正确格式化 From 头，符合 RFC5322 标准
        # Header().encode() 会将中文正确编码为符合 RFC2047 的格式
        encoded_sender_name = Header("金融分析小助手", "utf-8").encode()
        msg["From"] = formataddr((encoded_sender_name, smtp_user))
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
    def get_email_template(code: str) -> str:
        """
        获取邮件HTML模板

        Args:
            code: 验证码

        Returns:
            生成的HTML内容
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>验证码</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6; color: #1f2937; }}
        .container {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }}
        .header {{ background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 32px 20px; text-align: center; }}
        .header h1 {{ margin: 0; color: #ffffff; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content {{ padding: 40px 32px; text-align: center; }}
        .greeting {{ font-size: 18px; margin-bottom: 24px; color: #374151; font-weight: 500; }}
        .code-box {{ background: #eff6ff; border: 2px dashed #bfdbfe; border-radius: 12px; padding: 24px; margin: 32px 0; display: inline-block; min-width: 200px; }}
        .code {{ font-size: 36px; font-weight: 800; color: #1e40af; letter-spacing: 8px; font-family: 'Monaco', 'Menlo', 'Courier New', monospace; line-height: 1; }}
        .expiry {{ color: #6b7280; font-size: 14px; margin-top: 12px; }}
        .warning-box {{ background-color: #fff1f2; border-left: 4px solid #f43f5e; padding: 12px 16px; margin-top: 24px; text-align: left; border-radius: 0 4px 4px 0; }}
        .warning-text {{ color: #be123c; font-size: 13px; margin: 0; line-height: 1.5; }}
        .footer {{ background: #f9fafb; padding: 24px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af; }}
        .footer p {{ margin: 4px 0; }}
        .brand {{ color: #6b7280; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>智能金融数据平台</h1>
        </div>
        <div class="content">
            <p class="greeting">尊敬的用户</p>
            <p style="font-size: 15px; color: #4b5563; line-height: 1.6; margin-bottom: 10px;">
                您正在进行身份验证，请使用以下验证码完成操作。
            </p>
            <div class="code-box">
                <div class="code">{code}</div>
            </div>
            <p class="expiry">验证码将在 5 分钟后失效</p>

            <div class="warning-box">
                 <p class="warning-text"><strong>安全提示：</strong> 为了您的账号安全，请勿将此验证码告知他人。</p>
            </div>

            <p style="font-size: 14px; color: #9ca3af; margin-top: 30px;">
                如非本人操作，请忽略此邮件。
            </p>
        </div>
        <div class="footer">
            <p class="brand">Financial Data Platform</p>
            <p>此邮件由系统自动发送，请勿回复</p>
            <p>&copy; 2024 All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

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
