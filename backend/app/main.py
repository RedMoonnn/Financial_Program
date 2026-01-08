import logging
import os
import sys
from contextlib import asynccontextmanager
from threading import Thread

from api.middleware import exception_handler, logging_middleware
from api.v1.router import api_router
from core.logging import setup_logging
from crawler.crawler import start_crawler_job
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from services.init_db import init_db
from services.scheduler import init_scheduler
from starlette.exceptions import HTTPException as StarletteHTTPException

# 初始化日志配置
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"), log_file=os.getenv("LOG_FILE", None))

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - startup: 应用启动时执行
    - shutdown: 应用关闭时执行
    """
    # 启动时执行
    logger.info("应用启动中...")
    print("startup ok", file=sys.stderr, flush=True)

    # 启动爬虫任务
    Thread(target=start_crawler_job, daemon=True).start()

    # 启动定时任务调度器
    scheduler = init_scheduler()

    try:
        yield  # 应用运行期间
    finally:
        # 关闭时执行
        logger.info("应用关闭中...")
        if scheduler:
            scheduler.shutdown()
        # print("shutdown ok", file=sys.stderr, flush=True)


app = FastAPI(
    title="东方财富数据采集与分析平台API",
    docs_url="/docs",
    redoc_url="/redoc",
    description="金融数据采集、分析和AI智能分析平台",
    lifespan=lifespan,
)

# 注册异常处理器（顺序：先注册具体异常，最后注册通用异常）
app.add_exception_handler(RequestValidationError, exception_handler)
app.add_exception_handler(StarletteHTTPException, exception_handler)
app.add_exception_handler(Exception, exception_handler)

# 注册中间件（顺序很重要：先注册的会后执行）
app.middleware("http")(logging_middleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 注册所有路由模块 ====================
# 路由模块化组织，按功能分类，便于维护和扩展

app.include_router(api_router, prefix="/api/v1")  # 所有 v1 API 路由
# 保持向后兼容，同时注册旧路径
app.include_router(api_router, prefix="/api")  # 兼容旧路径

# 初始化数据库
init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
