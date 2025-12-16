"""
MinIO 存储 OP - 将分析报告存储到 MinIO
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dflow.python import OP, OPIO, OPIOSign, Artifact
from minio import Minio
from minio.error import S3Error


def get_now():
    """获取北京时间"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d_%H-%M-%S")


def get_minio_config():
    """获取 MinIO 配置（默认值与 .env 文件一致）"""
    return {
        "endpoint": os.getenv("MINIO_ENDPOINT", "minio:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "admin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "admin123"),
        "secure": os.getenv("MINIO_SECURE", "False").lower() in ["true", "1"],
    }


class StoreReportToMinIOOP(OP):
    """将分析报告存储到 MinIO"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "report_file": Artifact(Path),  # 分析报告文件
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "success": bool,
                "object_name": str,  # MinIO 中的对象名称
                "bucket": str,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        report_file = op_in["report_file"]

        # 获取 MinIO 配置
        config = get_minio_config()
        # 使用 MINIO_REPORT_BUCKET 或 MINIO_BUCKET
        bucket_name = os.getenv(
            "MINIO_REPORT_BUCKET", os.getenv("MINIO_BUCKET", "data-financial-agent")
        )

        # 生成对象名称（按日期组织）
        timestamp = get_now()
        object_name = f"analysis_reports/{timestamp}_report.json"

        try:
            # 创建 MinIO 客户端
            client = Minio(
                config["endpoint"],
                access_key=config["access_key"],
                secret_key=config["secret_key"],
                secure=config["secure"],
            )

            # 确保 bucket 存在
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)

            # 上传文件
            client.fput_object(
                bucket_name,
                object_name,
                str(report_file),
                content_type="application/json",
            )

            return OPIO(
                {
                    "success": True,
                    "object_name": object_name,
                    "bucket": bucket_name,
                }
            )

        except S3Error as e:
            print(f"MinIO 存储失败: {e}")
            return OPIO(
                {
                    "success": False,
                    "object_name": "",
                    "bucket": bucket_name,
                }
            )
        except Exception as e:
            print(f"存储失败: {e}")
            return OPIO(
                {
                    "success": False,
                    "object_name": "",
                    "bucket": bucket_name,
                }
            )
