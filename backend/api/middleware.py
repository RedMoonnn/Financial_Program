"""
API中间件模块
提供统一的异常处理、请求日志等功能
"""

import logging
import time
from typing import Callable

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from services.exceptions import ServiceException
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class APIResponse:
    """统一的API响应格式"""

    @staticmethod
    def success(data=None, message: str = "操作成功"):
        """成功响应"""
        return {"success": True, "message": message, "data": data}

    @staticmethod
    def error(message: str, code: int = 400, data=None):
        """错误响应"""
        return {"success": False, "message": message, "code": code, "data": data}


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    if isinstance(exc, ServiceException):
        logger.warning(f"业务异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=APIResponse.error(str(exc), code=400)
        )
    elif isinstance(exc, StarletteHTTPException):
        logger.warning(f"HTTP异常: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content=APIResponse.error(exc.detail, code=exc.status_code)
        )
    elif isinstance(exc, RequestValidationError):
        errors = exc.errors()
        error_msg = "; ".join([f"{err['loc']}: {err['msg']}" for err in errors])
        logger.warning(f"请求验证失败: {error_msg}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=APIResponse.error(f"请求参数错误: {error_msg}", code=422),
        )
    else:
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse.error("服务器内部错误", code=500),
        )


async def logging_middleware(request: Request, call_next: Callable):
    """请求日志中间件"""
    start_time = time.time()

    # 记录请求信息
    logger.info(
        f"请求开始: {request.method} {request.url.path} "
        f"客户端: {request.client.host if request.client else 'unknown'}"
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应信息
        logger.info(
            f"请求完成: {request.method} {request.url.path} "
            f"状态码: {response.status_code} "
            f"耗时: {process_time:.3f}s"
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"请求异常: {request.method} {request.url.path} "
            f"异常: {str(e)} "
            f"耗时: {process_time:.3f}s",
            exc_info=True,
        )
        raise
