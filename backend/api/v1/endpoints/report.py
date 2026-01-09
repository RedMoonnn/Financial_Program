"""
报告管理路由模块
"""

import json
import logging

from core.cache import get_redis_client
from core.storage import minio_storage
from fastapi import APIRouter, Body, Depends, Query
from services.ai import report
from services.report.report_service import ReportService

from api.middleware import APIResponse
from api.v1.endpoints.auth import get_current_user, is_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate")
async def generate_report_api(
    table_name: str = Body(..., description="表名"),
    chat_history: list = Body(..., description="聊天历史"),
    user=Depends(get_current_user),
):
    """
    生成报告

    - **table_name**: 表名
    - **chat_history**: 聊天历史记录
    """
    try:
        file_path, file_name, md_content, file_url = report.generate_report(
            table_name, chat_history, user_id=user.id
        )
        ReportService.add_report(user.id, "markdown", file_url, file_name)
        data = {"file_url": file_url, "file_name": file_name}
        return APIResponse.success(data=data, message="报告生成成功")
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        return APIResponse.error(message=f"生成报告失败: {str(e)}", code=500)


@router.get("/history")
def report_history(user=Depends(get_current_user)):
    """
    获取报告历史记录（从Redis）
    """
    try:
        r = get_redis_client()
        key = f"report:{user.id}"
        reports = r.lrange(key, 0, 19)  # 只取最近20条
        result = []
        for item in reports:
            try:
                result.append(json.loads(item))
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"解析报告历史记录失败: {item}")
                continue
        return APIResponse.success(data=result, message="获取报告历史成功")
    except Exception as e:
        logger.error(f"获取报告历史失败: {e}", exc_info=True)
        return APIResponse.success(data=[], message="获取报告历史成功")


@router.get("/minio_list")
def report_minio_list(user=Depends(get_current_user)):
    """
    获取报告文件列表
    - 管理员：返回所有用户的报告，包含用户信息
    - 普通用户：只返回自己的报告
    """
    try:
        admin_flag = is_admin_user(user)

        # 根据权限获取报告列表
        if admin_flag:
            reports = ReportService.list_all_reports()
        else:
            reports = ReportService.list_reports(user.id)

        # 获取用户信息映射（管理员需要显示报告所有者）
        user_map = {}
        if admin_flag:
            user_ids = {r.user_id for r in reports}
            user_map = ReportService.get_user_info_map(user_ids)

        result = []
        for r in reports:
            try:
                url = minio_storage.get_image_url(r.file_name)
            except Exception as e:
                logger.warning(f"获取文件URL失败: {r.file_name}, 错误: {e}")
                url = f"error: {e}"

            # 使用统一的转换函数
            report_dict = ReportService.report_to_dict(
                r, include_user=admin_flag, user_map=user_map
            )
            report_item = {
                "file_name": report_dict["file_name"],
                "url": url,
                "created_at": report_dict["created_at"],
            }

            # 管理员可以看到报告所有者信息
            if admin_flag:
                report_item["user_id"] = report_dict.get("user_id")
                report_item["user_email"] = report_dict.get("user_email")
                report_item["username"] = report_dict.get("username")

            result.append(report_item)

        return APIResponse.success(data=result, message="获取报告列表成功")
    except Exception as e:
        logger.error(f"[report_minio_list] 错误: {e}", exc_info=True)
        return APIResponse.success(data=[], message="获取报告列表成功")


@router.delete("/delete")
def report_delete(
    file_name: str = Query(..., description="文件名"),
    user=Depends(get_current_user),
):
    """
    删除报告文件
    - 管理员：可以删除任何报告
    - 普通用户：只能删除自己的报告

    - **file_name**: 要删除的文件名
    """
    try:
        admin_flag = is_admin_user(user)

        # 验证权限并删除数据库记录
        try:
            ReportService.delete_report(file_name, user.id, admin_flag)
        except PermissionError as e:
            return APIResponse.error(message=str(e), code=403)
        except Exception as e:
            logger.error(f"删除数据库记录失败: {e}", exc_info=True)
            return APIResponse.error(message=f"删除数据库记录失败: {str(e)}", code=500)

        # 删除MinIO中的文件
        try:
            bucket = minio_storage.bucket
            minio_storage.client.remove_object(bucket, file_name)
        except Exception as e:
            # 即使MinIO删除失败，数据库记录已删除，记录错误但不返回失败
            logger.error(f"删除MinIO文件失败: {file_name}, 错误: {e}", exc_info=True)

        return APIResponse.success(message=f"已删除 {file_name}")
    except Exception as e:
        logger.error(f"[report_delete] 错误: {e}", exc_info=True)
        return APIResponse.error(message=str(e), code=500)
