import os
from dotenv import load_dotenv
import redis
from minio import Minio
import requests

load_dotenv()

def check_redis():
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None),
            socket_connect_timeout=3
        )
        r.ping()
        print("[OK] Redis连接成功")
    except Exception as e:
        print(f"[FAIL] Redis连接失败: {e}")

def check_minio():
    try:
        client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=os.getenv('MINIO_SECURE', 'False').lower() in ['true', '1', 't']
        )
        buckets = client.list_buckets()
        print("[OK] MinIO连接成功，已存在桶:", [b.name for b in buckets])
    except Exception as e:
        print(f"[FAIL] MinIO连接失败: {e}")

def check_deepseek():
    try:
        url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com') + '/v1/finance/advice'  # 假设API路径
        headers = {
            'Authorization': f"Bearer {os.getenv('DEEPSEEK_API_KEY', '')}",
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-finance',
            'messages': [{"role": "user", "content": "测试连通性"}]
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("[OK] Deepseek API连通性正常")
        else:
            print(f"[FAIL] Deepseek API返回异常: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[FAIL] Deepseek API连接失败: {e}")

if __name__ == "__main__":
    print("==== 环境变量检测 ====")
    check_redis()
    check_minio()
    check_deepseek() 