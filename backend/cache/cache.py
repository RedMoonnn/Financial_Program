import redis
import os
from dotenv import load_dotenv

load_dotenv()


class RedisCache:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True,
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)

    def delete(self, key):
        self.client.delete(key)

    def close(self):
        self.client.close()


redis_cache = RedisCache()
