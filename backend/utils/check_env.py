import os
import socket

import pymysql
import redis
from dotenv import load_dotenv
from minio import Minio
from openai import OpenAI

# 加载.env
load_dotenv()

# 本地端口映射（与docker-compose.yml保持一致）
LOCAL_SERVICES = {
    "redis": {"host": "127.0.0.1", "port": 6379},
    "minio": {"host": "127.0.0.1", "port": 9002},  # API端口
    "minio_ui": {"host": "127.0.0.1", "port": 9001},  # 控制台
    "mysql": {"host": "127.0.0.1", "port": 3307},
}

# 环境变量
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "data_financial_agent")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() in ["true", "1", "t"]
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "mydb")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")


def check_socket(host, port, name):
    try:
        s = socket.create_connection((host, int(port)), timeout=3)
        s.close()
        print(f"[OK] {name} {host}:{port} 端口连通")
        return True
    except Exception as e:
        print(f"[FAIL] {name} {host}:{port} 端口无法连接: {e}")
        return False


def check_redis():
    host, port = LOCAL_SERVICES["redis"]["host"], LOCAL_SERVICES["redis"]["port"]
    if not check_socket(host, port, "Redis"):
        return
    try:
        r = redis.Redis(host=host, port=port, password=REDIS_PASSWORD, socket_connect_timeout=3)
        r.ping()
        print("[OK] Redis连接成功")
    except Exception as e:
        print(f"[FAIL] Redis连接失败: {e}")


def check_minio():
    host, port = LOCAL_SERVICES["minio"]["host"], LOCAL_SERVICES["minio"]["port"]
    if not check_socket(host, port, "MinIO API"):
        return
    try:
        client = Minio(
            f"{host}:{port}",
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        buckets = client.list_buckets()
        print(f"[OK] MinIO连接成功，已存在桶: {[b.name for b in buckets]}")
    except Exception as e:
        print(f"[FAIL] MinIO连接失败: {e}")
    # 检查WebUI端口
    host_ui, port_ui = (
        LOCAL_SERVICES["minio_ui"]["host"],
        LOCAL_SERVICES["minio_ui"]["port"],
    )
    check_socket(host_ui, port_ui, "MinIO 控制台")


def check_mysql():
    host, port = LOCAL_SERVICES["mysql"]["host"], LOCAL_SERVICES["mysql"]["port"]
    if not check_socket(host, port, "MySQL"):
        return
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            connect_timeout=3,
        )
        print("[OK] MySQL连接成功")
        conn.close()
    except Exception as e:
        print(f"[FAIL] MySQL连接失败: {e}")


def check_deepseek():
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False,
        )
        content = response.choices[0].message.content
        print(f"[OK] Deepseek API连通性正常，返回内容: {content}")
    except Exception as e:
        print(f"[FAIL] Deepseek API连接失败: {e}")


if __name__ == "__main__":
    print("==== 本地端口与服务连通性检测 ====")
    check_redis()
    check_minio()
    check_mysql()
    check_deepseek()
