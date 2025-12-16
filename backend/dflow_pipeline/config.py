"""
dflow 配置文件
"""
import os
from pathlib import Path
from dflow import config, s3_config

# 获取 backend 目录路径
BACKEND_DIR = str(Path(__file__).parent.parent.absolute())

# Argo Server 配置
config["host"] = os.getenv("ARGO_SERVER", "https://127.0.0.1:2746")
config["k8s_api_server"] = os.getenv("K8S_API_SERVER", "https://kubernetes.default.svc")
config["token"] = os.getenv("ARGO_TOKEN", "")

# Debug 模式配置 - 设置工作目录为 backend
config["debug_workdir"] = BACKEND_DIR

# S3/MinIO 配置 (artifact 存储)
s3_config["endpoint"] = os.getenv("MINIO_ENDPOINT", "minio:9000")
s3_config["access_key"] = os.getenv("MINIO_ACCESS_KEY", "admin")
s3_config["secret_key"] = os.getenv("MINIO_SECRET_KEY", "admin123")
s3_config["bucket"] = os.getenv("DFLOW_BUCKET", "dflow-artifacts")
s3_config["secure"] = os.getenv("MINIO_SECURE", "False").lower() in ["true", "1"]

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
    "charset": "utf8mb4",
}

# AI 配置
AI_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
}

# 采集配置
CRAWLER_CONFIG = {
    "base_url": "https://push2.eastmoney.com/api/qt/clist/get",
    "headers": {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "page_size": 50,
}
