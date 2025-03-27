# 保持热爱 奔赴山海
from dotenv import load_dotenv
import os
from minio import Minio
from minio.error import S3Error
import time


load_dotenv()  # 加载.env文件中的环境变量

def store_data_to_minio(title):

    # 记录运行开始时间
    start_time = time.time()


    # 图片文件路径
    image_path = f"./data/{title}/{title}.png"

    # 确保图片文件存在
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return  # 或者抛出异常

    # 读取图片文件为二进制数据
    try:
        with open(image_path, 'rb') as file:
            image_data = file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return  # 或者抛出异常

    # MinIO 连接配置
    minio_client = Minio(
        os.getenv('MINIO_ENDPOINT'),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        secure=bool(os.getenv('MINIO_SECURE', 'False').lower() in ['true', '1', 't'])
    )
    
    # 指定存储桶名称
    bucket_name = 'data'

    # 确保存储桶存在
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # 上传图片到 MinIO
    try:
        # 以二进制读模式打开本地图片文件（安全且自动管理文件关闭）
        with open(image_path, "rb") as file_data:
        # 获取文件元数据（包含文件大小、修改时间等信息）
            file_stat = os.stat(image_path)
            
            # 调用 MinIO SDK 的上传对象方法
            minio_client.put_object(
                bucket_name,          # 目标存储桶名称（已在 MinIO 创建好的"data"桶）
                f"{title}.png",       # 对象在 MinIO 中的唯一标识（此处用标题作为文件名）
                file_data,            # 文件数据流（通过 with open 获取的二进制数据）
                file_stat.st_size,    # 明确指定文件字节大小（确保完整传输）
                content_type="image/png"  # 声明文件 MIME 类型（影响浏览器预览行为）
            )

        # 记录结束时刻
        end_time = time.time()-start_time
        # print(f"Image uploaded to MinIO: {title}.png")

        print(f"MinIO\t: {end_time} seconds")
        # MinIO: Time taken: 0.19542455673217773 seconds

    except S3Error as e:
        print(f"Error uploading image to MinIO: {e}")

endpoint = os.getenv("MINIO_ENDPOINT")
print(f"Endpoint value: [{endpoint}]")