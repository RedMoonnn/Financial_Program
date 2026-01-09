import os

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
        [已弃用预签名URL] 改为返回后端代理下载地址

        弃用原因：
        1. 签名不匹配 (SignatureDoesNotMatch): Docker容器内(minio:9000)生成的签名基于内部Host，
           但在宿主机(localhost:9000)访问时Host不一致，导致MinIO拒绝请求。
        2. 网络隔离: 浏览器可能无法直接访问Docker内部网络中的MinIO地址。
        3. 浏览器行为: 预签名URL通常会导致浏览器尝试预览而不是下载。

        当前方案:
        返回指向后端 /api/v1/report/download 的代理接口。
        由后端在内网直接读取MinIO流并转发给前端，支持自定义文件名和强制下载。
        """
        import urllib.parse

        encoded_name = urllib.parse.quote(object_name)
        # 返回相对路径，前端配合API_BASE或直接使用
        return f"/api/v1/report/download?file_name={encoded_name}"

    def list_files(self, bucket=None):
        bucket = bucket or self.bucket
        objects = self.client.list_objects(bucket, recursive=True)
        return [obj.object_name for obj in objects]


minio_storage = MinioStorage()
