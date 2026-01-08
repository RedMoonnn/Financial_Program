"""
数据状态路由模块
"""

from fastapi import APIRouter
from services.common.cache_service import get_data_ready

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data_ready")
def data_ready():
    """
    检查数据是否就绪

    返回数据采集状态
    """
    return {"data_ready": get_data_ready()}
