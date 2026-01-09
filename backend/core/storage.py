import os
from datetime import timedelta
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from minio import Minio

load_dotenv()


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "False").lower() in ["true", "1", "t"],
        )
        self.bucket = os.getenv("MINIO_BUCKET", "data")
        # 公共端点：用于生成浏览器可访问的URL（如果设置了则使用，否则使用MINIO_ENDPOINT）
        self.public_endpoint = os.getenv(
            "MINIO_PUBLIC_ENDPOINT", os.getenv("MINIO_ENDPOINT", "localhost:9000")
        )
        # 确保存储桶存在
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_image(self, file_path, object_name=None):
        if not object_name:
            object_name = os.path.basename(file_path)
        file_stat = os.stat(file_path)
        with open(file_path, "rb") as f:
            self.client.put_object(
                self.bucket, object_name, f, file_stat.st_size, content_type="image/png"
            )
        return object_name

    def get_image_url(self, object_name):
        """
        生成预签名URL，默认1天有效
        如果设置了MINIO_PUBLIC_ENDPOINT，会将URL中的主机名替换为公共端点
        这样浏览器就可以访问了（例如：将 minio:9000 替换为 localhost:9000）
        """
        # 生成预签名URL
        url = self.client.presigned_get_object(
            self.bucket, object_name, expires=timedelta(seconds=60 * 60 * 24)
        )

        # 如果公共端点与内部端点不同，替换URL中的主机名
        internal_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        if self.public_endpoint != internal_endpoint:
            parsed = urlparse(url)
            # 替换主机名和端口
            new_netloc = self.public_endpoint
            # 保持协议（http/https）
            new_url = urlunparse(
                (
                    parsed.scheme,
                    new_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
            return new_url

        return url

    def list_files(self, bucket=None):
        bucket = bucket or self.bucket
        objects = self.client.list_objects(bucket, recursive=True)
        return [obj.object_name for obj in objects]


minio_storage = MinioStorage()
