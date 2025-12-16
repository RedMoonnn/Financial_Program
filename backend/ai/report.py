import os
from ai.deepseek import DeepseekAgent
from datetime import datetime, timedelta, timezone
from storage.storage import minio_storage


def chat_history_to_markdown(chat_history):
    md = ""
    # 清理历史对话，只保留有效对话
    cleaned_history = []
    for item in chat_history:
        question = item.get("question", "").strip()
        # 过滤掉过于简单的对话
        if (
            len(question) > 3
            and question.lower() not in ["你好", "hello", "hi", "test"]
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


def generate_report(table_name, chat_history):
    # 整理对话为md
    md_content = chat_history_to_markdown(chat_history)
    # 新prompt：直接生成最终结构化投资分析报告，不再要求补充，不嵌套markdown
    summary_prompt = (
        "你是一名专业金融分析师。请基于以下对话内容和资金流数据，直接生成一份完整、结构化、条理清晰、适合投资决策的最终资金流分析报告。"
        "报告必须包含：市场综述、资金流趋势、行业/板块表现、主力资金动向、风险提示、投资建议等。"
        "请直接输出最终Markdown正文，不要再嵌套任何markdown结构，也不要要求用户补充信息。"
        "\n\n" + md_content
    )
    summary = DeepseekAgent.analyze([], user_message=summary_prompt, style="专业")
    if isinstance(summary, dict) and "advice" in summary:
        summary_md = summary["advice"]
    else:
        summary_md = str(summary)
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
    return file_path, file_name, final_md, file_url
