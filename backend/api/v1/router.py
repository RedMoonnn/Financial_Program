"""
API v1 路由聚合
统一注册所有 v1 版本的端点
"""

from fastapi import APIRouter

from api.v1.endpoints import (
    ai,
    auth,
    collect,
    data,
    flow,
    health,
    report,
)

# 创建 v1 路由
api_router = APIRouter()

# 注册所有端点
# 注意：每个endpoint文件中的router已经定义了tags，这里不需要重复设置
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(flow.router)
api_router.include_router(ai.router)
api_router.include_router(report.router)
api_router.include_router(collect.router)
api_router.include_router(data.router)
