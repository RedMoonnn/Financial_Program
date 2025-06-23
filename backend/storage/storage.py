from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

load_dotenv()

class MinioStorage:
    def __init__(self):
        self.client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=os.getenv('MINIO_SECURE', 'False').lower() in ['true', '1', 't']
        )
        self.bucket = os.getenv('MINIO_BUCKET', 'data')
        # 确保存储桶存在
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_image(self, file_path, object_name=None):
        if not object_name:
            object_name = os.path.basename(file_path)
        file_stat = os.stat(file_path)
        with open(file_path, 'rb') as f:
            self.client.put_object(
                self.bucket,
                object_name,
                f,
                file_stat.st_size,
                content_type='image/png'
            )
        return object_name

    def get_image_url(self, object_name):
        # 生成预签名URL，默认1天有效
        return self.client.presigned_get_object(self.bucket, object_name, expires=60*60*24)

minio_storage = MinioStorage() 