from fastapi import FastAPI, Request, Query, Body, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from services.services import TaskService, FlowDataService, FlowImageService, CacheService, init_db, ChatService, ReportService
from crawler.crawler import fetch_flow_data
from api.health import health_bp
from ai.deepseek import DeepseekAgent
from typing import Optional
from api.auth import router as auth_router, get_current_user

app = FastAPI(title="东方财富数据采集与分析平台API", docs_url="/docs", redoc_url="/redoc")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册健康检查蓝图
app.include_router(health_bp)

# 注册auth路由
app.include_router(auth_router)

# 初始化数据库
init_db()

@app.post("/api/collect")
async def collect(
    flow_type: str = Body(...),
    market_type: str = Body(...),
    period: str = Body(...),
    pages: int = Body(1)
):
    try:
        task = TaskService.create_task(flow_type, market_type, period, pages)
        try:
            flow_data = fetch_flow_data(flow_type, market_type, period, pages)
            FlowDataService.save_flow_data(flow_data, task.id)
            for item in flow_data:
                CacheService.cache_flow_data(item['code'], flow_type, market_type, period, item)
            TaskService.update_task_status(task.id, 'success')
        except Exception as e:
            TaskService.update_task_status(task.id, 'failed', error_msg=str(e))
            raise HTTPException(status_code=500, detail={"error": "采集失败", "detail": str(e)})
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "参数错误", "detail": str(e)})

@app.get("/api/flow")
async def get_flow(
    code: str = Query(...),
    flow_type: str = Query(...),
    market_type: str = Query(...),
    period: str = Query(...)
):
    data = CacheService.get_cached_flow_data(code, flow_type, market_type, period)
    if data:
        return {"data": data, "cached": True}
    raise HTTPException(status_code=404, detail={"error": "未找到数据"})

@app.get("/api/image")
async def get_image(
    code: str = Query(...),
    flow_type: str = Query(...),
    market_type: str = Query(...),
    period: str = Query(...)
):
    url = CacheService.get_cached_image_url(code, flow_type, market_type, period)
    if url:
        return {"image_url": url, "cached": True}
    raise HTTPException(status_code=404, detail={"error": "未找到图片"})

@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    查询采集任务状态
    """
    from backend.models.models import SessionLocal, FlowTask
    session = SessionLocal()
    task = session.query(FlowTask).filter_by(id=task_id).first()
    if not task:
        session.close()
        return jsonify({'error': '任务不存在'}), 404
    result = {
        'id': task.id,
        'flow_type': task.flow_type,
        'market_type': task.market_type,
        'period': task.period,
        'pages': task.pages,
        'status': task.status.value,
        'start_time': str(task.start_time),
        'end_time': str(task.end_time) if task.end_time else None,
        'error_msg': task.error_msg
    }
    session.close()
    return jsonify(result)

@app.post("/api/ai/advice")
async def ai_advice(
    flow_type: str = Body(...),
    market_type: str = Body(...),
    period: str = Body(...),
    code: str = Body(...),
    style: str = Body("专业"),
    message: Optional[str] = Body(None),
    sector_flow_data: Optional[dict] = Body(None),
    user=Depends(get_current_user)
):
    try:
        flow_data = FlowDataService.get_latest_flow_data(code, flow_type, market_type, period)
        history = ChatService.get_history(user.id)
        result = DeepseekAgent.analyze(flow_data, sector_flow_data, style, message, history)
        # 追加本轮对话到历史
        history.append({"question": message, "answer": result})
        ChatService.save_history(user.id, history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@app.get("/api/report/list")
def report_list(user=Depends(get_current_user)):
    reports = ReportService.list_reports(user.id)
    return [{
        "id": r.id,
        "type": r.report_type,
        "file_url": r.file_url,
        "file_name": r.file_name,
        "created_at": str(r.created_at)
    } for r in reports]

@app.get("/api/report/download")
def report_download(report_id: int, user=Depends(get_current_user)):
    reports = ReportService.list_reports(user.id)
    for r in reports:
        if r.id == report_id:
            return {"file_url": r.file_url, "file_name": r.file_name}
    raise HTTPException(status_code=404, detail="报告不存在")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 