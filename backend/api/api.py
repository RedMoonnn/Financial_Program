from fastapi import FastAPI, Request, Query, Body, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from services.services import TaskService, FlowDataService, FlowImageService, CacheService, init_db, ChatService, ReportService, get_data_ready
from crawler.crawler import fetch_flow_data, run_collect, run_collect_all, start_crawler_job
from api.health import health_bp
from ai.deepseek import DeepseekAgent
from typing import Optional
from api.auth import router as auth_router, get_current_user
import traceback
import pymysql
import os
from datetime import datetime
from threading import Thread
import sys

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

# 东方财富采集参数与映射，参考 test_crawler/source_data_1.py
url = "https://push2.eastmoney.com/api/qt/clist/get"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
flows_id = [
    "jquery112309245886249999282_1733396772298",
    "jQuery112309570655592067874_1733410054611"
]
flows_names = ["Stock_Flow", "Sector_Flow"]
market_ids = [
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:23+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
    "m:0+t:80+f:!2",
    "m:1+t:3+f:!2",
    "m:0+t:7+f:!2"
]
market_names = [
    "All_Stocks", "SH&SZ_A_Shares", "SH_A_Shares", "STAR_Market", "SZ_A_Shares", "ChiNext_Market", "SH_B_Shares", "SZ_B_Shares"
]
detail_flows_ids = ["m:90+t:2", "m:90+t:3", "m:90+t:1"]
detail_flows_names = ["Industry_Flow", "Concept_Flow", "Regional_Flow"]
day1_ids = ["f62", "f267", "f164", "f174"]
day1_names = ["Today_Ranking", "3_Day_Ranking", "5_Day_Ranking", "10_Day_Ranking"]
day2_ids = ["f62", "f164", "f174"]
day2_names = ["Today_Ranking", "5_Day_Ranking", "10_Day_Ranking"]
fields_ids = [
    "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
    "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
    "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
    "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13"
]

# MySQL连接参数（容器内环境变量优先）
def get_db_config():
    return {
        'host': os.getenv('MYSQL_HOST', 'mysql'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', '123456'),
        'database': os.getenv('MYSQL_DATABASE', 'financial_web_crawler'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



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
    return {"data_ready": get_data_ready()}

# 新版API：单组合采集，调用crawler.py主函数
@app.post("/api/collect_v2")
async def collect_v2(
    flow_choice: int = Body(..., description="1:Stock_Flow, 2:Sector_Flow"),
    market_choice: int = Body(None, description="市场选项，仅flow_choice=1时有效"),
    detail_choice: int = Body(None, description="板块选项，仅flow_choice=2时有效"),
    day_choice: int = Body(..., description="日期选项"),
    pages: int = Body(1, description="采集页数")
):
    # 参数校验
    if flow_choice == 1:
        if market_choice is None or not (1 <= market_choice <= 8):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice=1时，market_choice必须为1~8")
        if day_choice not in [1,2,3,4]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="day_choice必须为1~4")
    elif flow_choice == 2:
        if detail_choice is None or not (1 <= detail_choice <= 3):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice=2时，detail_choice必须为1~3")
        if day_choice not in [1,2,3]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice=2时，day_choice必须为1~3")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice必须为1或2")
    result = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
    return result

# 新版API：全量采集，调用crawler.py主函数
@app.post("/api/collect_all_v2")
async def collect_all_v2(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_collect_all)
    return {"msg": "全量采集任务已启动"}

@app.on_event("startup")
def startup_event():
    print("startup ok", file=sys.stderr, flush=True)
    Thread(target=start_crawler_job, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 