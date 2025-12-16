"""
dflow 配置文件
"""

import os
from pathlib import Path
from dflow import config, s3_config

# 获取项目根目录和 backend 目录路径
BACKEND_DIR = Path(__file__).parent.parent.absolute()
PROJECT_ROOT = BACKEND_DIR.parent

# 加载 .env 文件
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # 只有当环境变量未设置时才从 .env 加载
                if key not in os.environ:
                    os.environ[key] = value

# dflow 工作目录 - 统一存放所有工作流产物
DFLOW_WORKDIR = BACKEND_DIR / ".dflow_workdir"
DFLOW_WORKDIR.mkdir(exist_ok=True)

# Argo Server 配置
config["host"] = os.getenv("ARGO_SERVER", "https://127.0.0.1:2746")
config["k8s_api_server"] = os.getenv("K8S_API_SERVER", "https://kubernetes.default.svc")
config["token"] = os.getenv("ARGO_TOKEN", "")

# Debug 模式配置 - 设置工作目录为统一的 .dflow_workdir
config["debug_workdir"] = str(DFLOW_WORKDIR)

# S3/MinIO 配置 (artifact 存储)
# 注意：dflow 客户端从本机提交，需要用 localhost:9000（通过 kubectl port-forward）
# Pod 内部访问用 minio:9000（K8s DNS）
# DFLOW_MINIO_* 专门用于 dflow 客户端连接 K8s 集群中的 MinIO
s3_config["endpoint"] = os.getenv("DFLOW_MINIO_ENDPOINT", "127.0.0.1:9000")
s3_config["access_key"] = os.getenv("DFLOW_MINIO_ACCESS_KEY", "admin")
s3_config["secret_key"] = os.getenv(
    "DFLOW_MINIO_SECRET_KEY", "password"
)  # K8s my-minio-cred 中的密码
s3_config["bucket"] = os.getenv("DFLOW_BUCKET", "my-bucket")
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
