import json
import os
from datetime import datetime, timedelta, timezone

from core.storage import minio_storage

from services.ai.deepseek import DeepseekAgent


def chat_history_to_markdown(chat_history):
    md = ""
    # 清理历史对话，只保留有效对话
    cleaned_history = []
    for item in chat_history:
        question = item.get("question", "").strip()
        # 过滤掉过于简单的对话
        if (
            len(question) > 3
            and question.lower() not in ["你是谁", "你好", "hello", "hi", "test"]
            and not question.startswith("你好")
        ):
            cleaned_history.append(item)
    # 只保留最近的10条有效对话
    cleaned_history = cleaned_history[-10:]
    for idx, item in enumerate(cleaned_history, 1):
        md += f"### 问答{idx}\n"
        md += f"**你：** {item['question']}\n\n"
        ai_ans = (
            item["answer"]["advice"]
            if isinstance(item["answer"], dict) and "advice" in item["answer"]
            else str(item["answer"])
        )
        md += f"**AI：** {ai_ans}\n\n"
    return md


def generate_report(table_name, chat_history, user_id=None):
    # 整理对话为md
    md_content = chat_history_to_markdown(chat_history)
    # 新prompt：直接生成最终结构化投资分析报告，不再要求补充，不嵌套markdown
    summary_prompt = (
        "你是一名专业金融分析师。请基于以下对话内容和资金流数据，直接生成一份完整、结构化、条理清晰、适合投资决策的最终资金流分析报告。"
        "报告必须包含：市场综述、资金流趋势、行业/板块表现、主力资金动向、风险提示、投资建议等。"
        "请直接输出最终Markdown正文，不要再嵌套任何markdown结构，也不要要求用户补充信息。"
        "\n\n" + md_content
    )
    # 使用 deepseek-chat 模型加快响应速度（非推理模型，速度更快）
    system_message = "你是一名专业金融分析师，善于资金流分析和投资建议。"
    summary_md = DeepseekAgent.chat(
        user_message=summary_prompt, system_message=system_message, stream=False
    )
    # 合并原始对话和AI总结
    final_md = f"{md_content}\n---\n{summary_md}"
    # 使用东八区时间
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz).strftime("%Y%m%d_%H%M%S")
    file_name = f"report_{table_name}_{now}.md"
    file_path = os.path.join("/tmp", file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_md)
    # 上传到MinIO
    object_name = minio_storage.upload_image(file_path, file_name)
    file_url = minio_storage.get_image_url(object_name)
    # 存储到Redis（如有user_id）
    try:
        if user_id:
            from redis import Redis

            redis_kwargs = {
                "host": os.getenv("REDIS_HOST", "redis"),
                "port": int(os.getenv("REDIS_PORT", 6379)),
                "decode_responses": True,
            }
            redis_pwd = os.getenv("REDIS_PASSWORD")
            if redis_pwd:
                redis_kwargs["password"] = redis_pwd
            r = Redis(**redis_kwargs)
            r.lpush(
                f"report:{user_id}",
                json.dumps({"url": file_url, "file_name": file_name, "created_at": now}),
            )
    except Exception as e:
        print(f"[report.py] Redis存储报告路径失败: {e}")
    return file_path, file_name, final_md, file_url
