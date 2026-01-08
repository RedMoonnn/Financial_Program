"""
报告管理路由模块
"""

import json

import redis
from core.config import REDIS_CONFIG
from core.storage import minio_storage
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from services.ai import report
from services.report.report_service import ReportService

from api.v1.endpoints.auth import get_admin_user, get_current_user

router = APIRouter(prefix="/api/report", tags=["report"])


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
def report_minio_list(admin_user=Depends(get_admin_user)):
    """
    获取MinIO中的报告文件列表（需要管理员权限）
    """
    try:
        bucket = minio_storage.bucket
        files = minio_storage.list_files(bucket)
        result = []
        for f in files:
            if f.endswith(".md"):
                try:
                    url = minio_storage.get_image_url(f)
                except Exception as e:
                    url = f"error: {e}"
                result.append({"file_name": f, "url": url})
        return result
    except Exception as e:
        print(f"[report_minio_list] error: {e}")
        return []


@router.delete("/delete")
def report_delete(
    file_name: str = Query(..., description="文件名"),
    admin_user=Depends(get_admin_user),  # 需要管理员权限
):
    """
    删除报告文件（需要管理员权限）

    - **file_name**: 要删除的文件名
    """
    try:
        bucket = minio_storage.bucket
        minio_storage.client.remove_object(bucket, file_name)
        return {"success": True, "msg": f"已删除 {file_name}"}
    except Exception as e:
        return {"success": False, "msg": str(e)}
