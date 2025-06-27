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
    code: Optional[str] = Query(None),
    flow_type: str = Query(...),
    market_type: str = Query(...),
    period: str = Query(...)
):
    from services.services import SessionLocal, FlowData
    session = SessionLocal()
    if code:
        data = session.query(FlowData).filter_by(code=code, flow_type=flow_type, market_type=market_type, period=period).all()
    else:
        data = session.query(FlowData).filter_by(flow_type=flow_type, market_type=market_type, period=period).all()
    session.close()
    if data:
        # 转为dict数组
        result = [
            {
                'code': d.code,
                'name': d.name,
                'flow_type': d.flow_type,
                'market_type': d.market_type,
                'period': d.period,
                'latest_price': d.latest_price,
                'change_percentage': d.change_percentage,
                'main_flow_net_amount': d.main_flow_net_amount,
                'main_flow_net_percentage': d.main_flow_net_percentage,
                'extra_large_order_flow_net_amount': d.extra_large_order_flow_net_amount,
                'extra_large_order_flow_net_percentage': d.extra_large_order_flow_net_percentage,
                'large_order_flow_net_amount': d.large_order_flow_net_amount,
                'large_order_flow_net_percentage': d.large_order_flow_net_percentage,
                'medium_order_flow_net_amount': d.medium_order_flow_net_amount,
                'medium_order_flow_net_percentage': d.medium_order_flow_net_percentage,
                'small_order_flow_net_amount': d.small_order_flow_net_amount,
                'small_order_flow_net_percentage': d.small_order_flow_net_percentage,
                'crawl_time': str(d.crawl_time)
            } for d in data
        ]
        return {"data": result, "cached": False}
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
    message: str = Body(...),
    context: Optional[dict] = Body(None),
    user=Depends(get_current_user)
):
    try:
        # context中包含marketType, flowType, period, tableData等
        flow_data = context.get('tableData') if context else None
        style = "专业"
        history = ChatService.get_history(user.id)
        result = DeepseekAgent.analyze(flow_data, None, style, message, history)
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

@app.get("/api/data_ready")
def data_ready():
    from services.services import DATA_READY
    return {"data_ready": DATA_READY}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 