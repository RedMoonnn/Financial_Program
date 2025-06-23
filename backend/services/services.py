from backend.config import Config
from backend.models.models import Base, FlowTask, FlowData, FlowImage, TaskStatus
from backend.cache.cache import redis_cache
from backend.storage.storage import minio_storage
from backend.utils.utils import get_now
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# 创建数据库引擎和会话工厂
engine = create_engine(
    f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}?charset=utf8mb4",
    echo=False
)
SessionLocal = sessionmaker(bind=engine)

# 初始化数据库（如首次运行需建表）
def init_db():
    Base.metadata.create_all(engine)

# 1. 采集任务相关服务
class TaskService:
    @staticmethod
    def create_task(flow_type, market_type, period, pages):
        session = SessionLocal()
        task = FlowTask(
            flow_type=flow_type,
            market_type=market_type,
            period=period,
            pages=pages,
            status=TaskStatus.pending,
            start_time=get_now()
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        session.close()
        return task

    @staticmethod
    def update_task_status(task_id, status, error_msg=None):
        session = SessionLocal()
        task = session.query(FlowTask).filter_by(id=task_id).first()
        if task:
            task.status = status
            task.end_time = get_now()
            if error_msg:
                task.error_msg = error_msg
            session.commit()
        session.close()

# 2. 资金流数据入库服务
class FlowDataService:
    @staticmethod
    def save_flow_data(data_list, task_id):
        session = SessionLocal()
        for data in data_list:
            flow_data = FlowData(
                code=data['code'],
                name=data['name'],
                flow_type=data['flow_type'],
                market_type=data['market_type'],
                period=data['period'],
                latest_price=data.get('latest_price'),
                change_percentage=data.get('change_percentage'),
                main_flow_net_amount=data.get('main_flow_net_amount'),
                main_flow_net_percentage=data.get('main_flow_net_percentage'),
                extra_large_order_flow_net_amount=data.get('extra_large_order_flow_net_amount'),
                extra_large_order_flow_net_percentage=data.get('extra_large_order_flow_net_percentage'),
                large_order_flow_net_amount=data.get('large_order_flow_net_amount'),
                large_order_flow_net_percentage=data.get('large_order_flow_net_percentage'),
                medium_order_flow_net_amount=data.get('medium_order_flow_net_amount'),
                medium_order_flow_net_percentage=data.get('medium_order_flow_net_percentage'),
                small_order_flow_net_amount=data.get('small_order_flow_net_amount'),
                small_order_flow_net_percentage=data.get('small_order_flow_net_percentage'),
                crawl_time=get_now(),
                task_id=task_id
            )
            session.merge(flow_data)  # merge可避免唯一索引冲突
        session.commit()
        session.close()

    @staticmethod
    def get_latest_flow_data(code, flow_type, market_type, period):
        session = SessionLocal()
        q = session.query(FlowData).filter_by(
            code=code,
            flow_type=flow_type,
            market_type=market_type,
            period=period
        ).order_by(FlowData.crawl_time.desc())
        result = q.first()
        session.close()
        if result:
            return {
                'code': result.code,
                'name': result.name,
                'flow_type': result.flow_type,
                'market_type': result.market_type,
                'period': result.period,
                'latest_price': result.latest_price,
                'change_percentage': result.change_percentage,
                'main_flow_net_amount': result.main_flow_net_amount,
                'main_flow_net_percentage': result.main_flow_net_percentage,
                'extra_large_order_flow_net_amount': result.extra_large_order_flow_net_amount,
                'extra_large_order_flow_net_percentage': result.extra_large_order_flow_net_percentage,
                'large_order_flow_net_amount': result.large_order_flow_net_amount,
                'large_order_flow_net_percentage': result.large_order_flow_net_percentage,
                'medium_order_flow_net_amount': result.medium_order_flow_net_amount,
                'medium_order_flow_net_percentage': result.medium_order_flow_net_percentage,
                'small_order_flow_net_amount': result.small_order_flow_net_amount,
                'small_order_flow_net_percentage': result.small_order_flow_net_percentage,
                'crawl_time': str(result.crawl_time)
            }
        return None

# 3. 图片上传与元数据入库服务
class FlowImageService:
    @staticmethod
    def save_image(file_path, code, flow_type, market_type, period, task_id):
        # 上传图片到MinIO
        object_name = minio_storage.upload_image(file_path)
        image_url = minio_storage.get_image_url(object_name)
        session = SessionLocal()
        flow_image = FlowImage(
            code=code,
            flow_type=flow_type,
            market_type=market_type,
            period=period,
            image_url=image_url,
            crawl_time=get_now(),
            task_id=task_id
        )
        session.merge(flow_image)
        session.commit()
        session.close()
        return image_url

# 4. Redis缓存服务
class CacheService:
    @staticmethod
    def cache_flow_data(code, flow_type, market_type, period, data, expire=3600):
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        redis_cache.set(key, json.dumps(data), ex=expire)

    @staticmethod
    def get_cached_flow_data(code, flow_type, market_type, period):
        key = f"flow:{code}:{flow_type}:{market_type}:{period}"
        value = redis_cache.get(key)
        if value:
            return json.loads(value)
        return None

    @staticmethod
    def cache_image_url(code, flow_type, market_type, period, url, expire=3600):
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        redis_cache.set(key, url, ex=expire)

    @staticmethod
    def get_cached_image_url(code, flow_type, market_type, period):
        key = f"flowimg:{code}:{flow_type}:{market_type}:{period}"
        return redis_cache.get(key) 