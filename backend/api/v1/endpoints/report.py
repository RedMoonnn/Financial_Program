"""
报告管理路由模块
"""

import json

import redis
from core.config import REDIS_CONFIG
from core.database import get_db_session
from core.storage import minio_storage
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from models.models import User
from services.ai import report
from services.report.report_service import ReportService

from api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/list")
def report_list(user=Depends(get_current_user)):
    """
    获取用户的报告列表
    """
    reports = ReportService.list_reports(user.id)
    return [
        {
            "id": r.id,
            "type": r.report_type,
            "file_url": r.file_url,
            "file_name": r.file_name,
            "created_at": str(r.created_at),
        }
        for r in reports
    ]


@router.get("/download")
def report_download(
    report_id: int = Query(..., description="报告ID"), user=Depends(get_current_user)
):
    """
    下载报告

    - **report_id**: 报告ID
    """
    reports = ReportService.list_reports(user.id)
    for r in reports:
        if r.id == report_id:
            return {"file_url": r.file_url, "file_name": r.file_name}
    raise HTTPException(status_code=404, detail="报告不存在")


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
        return {"success": True, "file_url": file_url, "file_name": file_name}
    except Exception as e:
        import traceback

        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


@router.get("/history")
def report_history(user=Depends(get_current_user)):
    """
    获取报告历史记录（从Redis）
    """
    try:
        r = redis.Redis(**REDIS_CONFIG)
        key = f"report:{user.id}"
        reports = r.lrange(key, 0, 19)  # 只取最近20条
        result = []
        for item in reports:
            try:
                result.append(json.loads(item))
            except Exception:
                continue
        return result
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"获取报告历史失败: {e}", exc_info=True)
        return []


@router.get("/minio_list")
def report_minio_list(user=Depends(get_current_user)):
    """
    获取报告文件列表
    - 管理员：返回所有用户的报告，包含用户信息
    - 普通用户：只返回自己的报告
    """
    try:
        is_admin = user.is_admin == 1

        # 根据权限获取报告列表
        if is_admin:
            reports = ReportService.list_all_reports()
        else:
            reports = ReportService.list_reports(user.id)

        # 获取用户信息映射（管理员需要显示报告所有者）
        user_map = {}
        if is_admin:
            with get_db_session() as session:
                user_ids = {r.user_id for r in reports}
                users = session.query(User).filter(User.id.in_(user_ids)).all()
                user_map = {
                    u.id: {"id": u.id, "email": u.email, "username": u.username} for u in users
                }

        result = []
        for r in reports:
            try:
                url = minio_storage.get_image_url(r.file_name)
            except Exception as e:
                url = f"error: {e}"

            report_item = {
                "file_name": r.file_name,
                "url": url,
                "created_at": str(r.created_at) if r.created_at else None,
            }

            # 管理员可以看到报告所有者信息
            if is_admin:
                owner = user_map.get(r.user_id, {})
                report_item["user_id"] = r.user_id
                report_item["user_email"] = owner.get("email", "未知")
                report_item["username"] = owner.get("username")

            result.append(report_item)

        return result
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"[report_minio_list] error: {e}", exc_info=True)
        return []


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
        is_admin = user.is_admin == 1

        # 验证权限并删除数据库记录
        try:
            ReportService.delete_report(file_name, user.id, is_admin)
        except PermissionError as e:
            return {"success": False, "msg": str(e)}
        except Exception as e:
            return {"success": False, "msg": f"删除数据库记录失败: {str(e)}"}

        # 删除MinIO中的文件
        try:
            bucket = minio_storage.bucket
            minio_storage.client.remove_object(bucket, file_name)
        except Exception as e:
            # 即使MinIO删除失败，数据库记录已删除，记录错误但不返回失败
            import logging

            logging.getLogger(__name__).error(f"删除MinIO文件失败: {e}", exc_info=True)

        return {"success": True, "msg": f"已删除 {file_name}"}
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"[report_delete] error: {e}", exc_info=True)
        return {"success": False, "msg": str(e)}
