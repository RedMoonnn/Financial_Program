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
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(flow.router, tags=["flow"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(report.router, tags=["report"])
api_router.include_router(collect.router, tags=["collect"])
api_router.include_router(data.router, tags=["data"])
