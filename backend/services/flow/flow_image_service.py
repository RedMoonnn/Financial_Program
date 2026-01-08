"""
图片服务模块
处理图片上传和元数据管理
"""

import logging

from core.database import get_db_session
from core.storage import minio_storage
from models.models import FlowImage
from utils.utils import get_now

logger = logging.getLogger(__name__)


class FlowImageService:
    """图片服务类"""

    @staticmethod
    def save_image(
        file_path: str, code: str, flow_type: str, market_type: str, period: str, task_id: int
    ) -> str:
        """
        保存图片并上传到MinIO

        Args:
            file_path: 本地文件路径
            code: 股票代码
            flow_type: 资金流类型
            market_type: 市场类型
            period: 周期
            task_id: 关联的任务ID

        Returns:
            图片URL
        """
        # 上传图片到MinIO
        object_name = minio_storage.upload_image(file_path)
        image_url = minio_storage.get_image_url(object_name)

        # 保存元数据到数据库
        with get_db_session() as session:
            flow_image = FlowImage(
                code=code,
                flow_type=flow_type,
                market_type=market_type,
                period=period,
                image_url=image_url,
                crawl_time=get_now(),
                task_id=task_id,
            )
            session.merge(flow_image)
            logger.info(f"图片已保存: {image_url} (任务ID: {task_id})")

        return image_url
