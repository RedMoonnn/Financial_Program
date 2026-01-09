"""
AI分析路由模块
"""

import json
import sys
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])


async def generate_stream_response(flow_data, user_message, style, history=None):
    """
    生成流式响应的异步生成器函数
    使用 SSE (Server-Sent Events) 格式
    """
    try:
        from services.ai.deepseek import DeepseekAgent

        # 使用流式分析方法
        stream = DeepseekAgent.analyze_stream(
            flow_data, user_message=user_message, history=history, style=style
        )

        for chunk in stream:
            # 将数据格式化为 SSE 格式
            data = json.dumps(chunk, ensure_ascii=False)
            yield f"data: {data}\n\n"

        # 发送结束标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        import traceback

        error_msg = f"流式输出错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr, flush=True)
        error_chunk = {"type": "error", "content": str(e)}
        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/advice")
async def ai_advice(
    message: str = Body(..., description="用户问题"),
    context: Optional[dict] = Body(None, description="上下文信息"),
    table_name: Optional[str] = Body(None, description="可选，指定要分析的数据库表名"),
    history: Optional[list] = Body(None, description="历史对话记录"),
    stream: bool = Body(False, description="是否使用流式输出"),
    user=Depends(get_current_user),
):
    """
    AI智能分析建议

    - **message**: 用户问题
    - **table_name**: 可选，指定要分析的数据库表名
    - **history**: 可选，历史对话记录
    - **stream**: 是否使用流式输出（默认False）
    """
    try:
        print(
            f"AI advice called with message: {message}, user_id: {user.id}, table_name: {table_name}, stream: {stream}",
            file=sys.stderr,
            flush=True,
        )

        from services.flow.flow_data_query import query_table_data

        style = "专业"
        flow_data = []

        # 场景一：前端传了表名，查该表
        if table_name:
            flow_data = query_table_data(table_name, limit=50)
            if not flow_data:
                error_response = {
                    "advice": "数据缺失",
                    "reasons": [f"数据库中未找到表 {table_name} 或无数据，请检查表名或采集流程。"],
                    "risks": [],
                    "detail": f"请检查爬虫采集与入库流程，确保 {table_name} 有数据。",
                }

                # 流式返回错误
                async def error_stream():
                    error_chunk = {
                        "type": "error",
                        "content": json.dumps(error_response, ensure_ascii=False),
                    }
                    yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"

                return StreamingResponse(
                    error_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )

            # 只传递核心字段，防止token溢出
            slim_data = []
            for d in flow_data:
                # Use .get() for safer access, provide defaults if needed
                item_data = d.get("data", {})
                slim_data.append(
                    {
                        "type": d.get("type"),
                        "flow_type": d.get("flow_type"),
                        "market_type": d.get("market_type"),
                        "period": d.get("period"),
                        "data": {
                            "code": item_data.get("code"),
                            "name": item_data.get("name"),
                            "main_flow_net_amount": item_data.get("main_flow_net_amount"),
                            "main_flow_net_percentage": item_data.get("main_flow_net_percentage"),
                            "change_percentage": item_data.get("change_percentage"),
                            "crawl_time": item_data.get("crawl_time"),
                        },
                    }
                )
            user_message = message or f"请帮我分析一下表 {table_name} 的资金流情况"

            return StreamingResponse(
                generate_stream_response(slim_data, user_message, style, history),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )

        # 场景二：未传表名，进行通用问答
        user_message = message

        return StreamingResponse(
            generate_stream_response(flow_data, user_message, style, history),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        import traceback

        error_msg = f"AI advice error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail={"error": str(e)}) from e
