from fastapi import (
    FastAPI,
    Query,
    Body,
    HTTPException,
    BackgroundTasks,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from services.services import init_db, ReportService, get_data_ready
from crawler.crawler import run_collect, run_collect_all, start_crawler_job
from api.health import health_bp
from typing import Optional
import pymysql
import os
from datetime import datetime
from threading import Thread
import sys
from ai import report
from redis import Redis
import json
import re
from storage.storage import minio_storage

# 允许的表名模式（防止SQL注入）
VALID_TABLE_PATTERN = re.compile(r"^(Stock_Flow|Sector_Flow)_[A-Za-z0-9_&]+$")


def validate_table_name(table_name: str) -> bool:
    """验证表名是否合法，防止SQL注入"""
    return bool(VALID_TABLE_PATTERN.match(table_name))


app = FastAPI(
    title="东方财富数据采集与分析平台API", docs_url="/docs", redoc_url="/redoc"
)

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

# 初始化数据库
init_db()

# 东方财富采集参数与映射，参考 test_crawler/source_data_1.py
url = "https://push2.eastmoney.com/api/qt/clist/get"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
flows_id = [
    "jquery112309245886249999282_1733396772298",
    "jQuery112309570655592067874_1733410054611",
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
    "m:0+t:7+f:!2",
]
market_names = [
    "All_Stocks",
    "SH&SZ_A_Shares",
    "SH_A_Shares",
    "STAR_Market",
    "SZ_A_Shares",
    "ChiNext_Market",
    "SH_B_Shares",
    "SZ_B_Shares",
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
    "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
]


# MySQL连接参数（容器内环境变量优先）
def get_db_config():
    return {
        "host": os.getenv("MYSQL_HOST", "mysql"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "123456"),
        "database": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "charset": "utf8mb4",
    }


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.get("/api/flow")
async def get_flow(
    flow_type: str = Query(...), market_type: str = Query(...), period: str = Query(...)
):
    table_name = f"{flow_type}_{market_type}_{period}".replace("-", "_")
    # 验证表名防止SQL注入
    if not validate_table_name(table_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="非法表名格式"
        )
    db_config = get_db_config()
    print(f"API查表名: {table_name}", file=sys.stderr, flush=True)
    print(f"API数据库名: {db_config['database']}", file=sys.stderr, flush=True)
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        if not cursor.fetchone():
            print(f"表不存在: {table_name}", file=sys.stderr, flush=True)
            return {"data": [], "cached": False, "error": "未找到数据表"}
        cursor.execute(
            f"SELECT * FROM `{table_name}` ORDER BY crawl_time DESC LIMIT 100"
        )
        rows = cursor.fetchall()
        print(f"查到数据条数: {len(rows)}", file=sys.stderr, flush=True)
        return {"data": rows, "cached": False}
    except Exception as e:
        print(f"查表异常: {e}", file=sys.stderr, flush=True)
        return {"data": [], "cached": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/ai/advice")
async def ai_advice(
    message: str = Body(...),
    context: Optional[dict] = Body(None),
    table_name: Optional[str] = Body(None, description="可选，指定要分析的数据库表名"),
):
    try:
        print(
            f"AI advice called with message: {message}, table_name: {table_name}",
            file=sys.stderr,
            flush=True,
        )
        from services.flow_data_query import query_table_data
        from ai.deepseek import DeepseekAgent

        style = "专业"
        flow_data = []
        # 场景一：前端传了表名，查该表
        if table_name:
            flow_data = query_table_data(table_name, limit=50)
            if not flow_data:
                return {
                    "advice": "数据缺失",
                    "reasons": [
                        f"数据库中未找到表 {table_name} 或无数据，请检查表名或采集流程。"
                    ],
                    "risks": [],
                    "detail": f"请检查爬虫采集与入库流程，确保 {table_name} 有数据。",
                }
            # 只传递核心字段，防止token溢出
            slim_data = [
                {
                    "type": d["type"],
                    "flow_type": d["flow_type"],
                    "market_type": d["market_type"],
                    "period": d["period"],
                    "data": {
                        "code": d["data"]["code"],
                        "name": d["data"]["name"],
                        "main_flow_net_amount": d["data"]["main_flow_net_amount"],
                        "main_flow_net_percentage": d["data"][
                            "main_flow_net_percentage"
                        ],
                        "change_percentage": d["data"]["change_percentage"],
                        "crawl_time": d["data"]["crawl_time"],
                    },
                }
                for d in flow_data
            ]
            user_message = message or f"请帮我分析一下表 {table_name} 的资金流情况"
            result = DeepseekAgent.analyze(
                slim_data, user_message=user_message, style=style
            )
            if isinstance(result, dict):
                return result
            else:
                return {"answer": result}
        # 兼容原有逻辑（未传表名时）
        # ... existing code ...
    except Exception as e:
        import traceback

        error_msg = f"AI advice error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/api/ai/advice/stream")
async def ai_advice_stream(
    message: str = Body(...),
    context: Optional[dict] = Body(None),
    table_name: Optional[str] = Body(None, description="可选，指定要分析的数据库表名"),
):
    """
    流式输出AI分析结果，使用Server-Sent Events (SSE)
    """
    from services.flow_data_query import query_table_data
    from ai.deepseek import DeepseekAgent

    async def generate():
        try:
            print(
                f"AI stream advice called with message: {message}, table_name: {table_name}",
                file=sys.stderr,
                flush=True,
            )
            style = "专业"
            flow_data = []

            if table_name:
                flow_data = query_table_data(table_name, limit=50)
                if not flow_data:
                    yield f"data: 数据库中未找到表 {table_name} 或无数据，请检查表名或采集流程。\n\n"
                    yield "data: [DONE]\n\n"
                    return

                # 只传递核心字段，防止token溢出
                slim_data = [
                    {
                        "type": d["type"],
                        "flow_type": d["flow_type"],
                        "market_type": d["market_type"],
                        "period": d["period"],
                        "data": {
                            "code": d["data"]["code"],
                            "name": d["data"]["name"],
                            "main_flow_net_amount": d["data"]["main_flow_net_amount"],
                            "main_flow_net_percentage": d["data"][
                                "main_flow_net_percentage"
                            ],
                            "change_percentage": d["data"]["change_percentage"],
                            "crawl_time": d["data"]["crawl_time"],
                        },
                    }
                    for d in flow_data
                ]

                user_message = message or f"请帮我分析一下表 {table_name} 的资金流情况"

                # 使用流式输出
                for chunk in DeepseekAgent.analyze_stream(
                    slim_data, user_message=user_message, style=style
                ):
                    # SSE格式：data: <内容>\n\n
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

                yield "data: [DONE]\n\n"
            else:
                yield "data: 请指定要分析的表名\n\n"
                yield "data: [DONE]\n\n"

        except Exception as e:
            import traceback

            error_msg = f"AI stream error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr, flush=True)
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/report/list")
def report_list():
    reports = ReportService.list_reports()
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


@app.get("/api/report/download")
def report_download(report_id: int):
    reports = ReportService.list_reports()
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
    pages: int = Body(1, description="采集页数"),
):
    """
    采集数据并返回：
    - table: 表名
    - count: 采集条数
    - crawl_time: 采集时间
    - data: 采集到的全部数据（用于前端Echarts实时渲染）
    """
    # 参数校验
    if flow_choice == 1:
        if market_choice is None or not (1 <= market_choice <= 8):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=1时，market_choice必须为1~8",
            )
        if day_choice not in [1, 2, 3, 4]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="day_choice必须为1~4"
            )
    elif flow_choice == 2:
        if detail_choice is None or not (1 <= detail_choice <= 3):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=2时，detail_choice必须为1~3",
            )
        if day_choice not in [1, 2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=2时，day_choice必须为1~3",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice必须为1或2"
        )
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


@app.post("/api/report/generate")
async def generate_report_api(
    table_name: str = Body(...),
    chat_history: list = Body(...),
):
    try:
        file_path, file_name, md_content, file_url = report.generate_report(
            table_name, chat_history
        )
        from services.services import ReportService

        ReportService.add_report("markdown", file_url, file_name)
        return {"success": True, "file_url": file_url, "file_name": file_name}
    except Exception as e:
        import traceback

        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


@app.get("/api/report/history")
def report_history():
    try:
        r = Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True,
        )
        key = "report:history"
        reports = r.lrange(key, 0, 19)  # 只取最近20条
        result = []
        for item in reports:
            try:
                result.append(json.loads(item))
            except Exception:
                continue
        return result
    except Exception:
        return []


@app.get("/api/report/minio_list")
def report_minio_list():
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


@app.delete("/api/report/delete")
def report_delete(file_name: str):
    try:
        bucket = minio_storage.bucket
        minio_storage.client.remove_object(bucket, file_name)
        return {"success": True, "msg": f"已删除 {file_name}"}
    except Exception as e:
        return {"success": False, "msg": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
