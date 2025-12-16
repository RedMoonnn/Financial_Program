"""
报告生成 OP - 生成分析报告并上传到 MinIO
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dflow.python import OP, OPIO, OPIOSign, Artifact
from openai import OpenAI
from minio import Minio


class GenerateReportOP(OP):
    """生成分析报告 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            "table_name": str,
            "chat_history": str,  # JSON 字符串
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            "report_file": Artifact(Path),
            "report_url": str,
            "file_name": str,
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        table_name = op_in["table_name"]
        chat_history = json.loads(op_in["chat_history"])

        # 生成报告内容
        md_content = self._chat_history_to_markdown(chat_history)
        summary = self._generate_summary(md_content)
        final_md = f"{md_content}\n---\n{summary}"

        # 生成文件名
        beijing_tz = timezone(timedelta(hours=8))
        now = datetime.now(beijing_tz).strftime("%Y%m%d_%H%M%S")
        file_name = f"report_{table_name}_{now}.md"

        # 保存文件
        file_path = Path(f"/tmp/{file_name}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_md)

        # 上传到 MinIO
        report_url = self._upload_to_minio(file_path, file_name)

        return OPIO({
            "report_file": file_path,
            "report_url": report_url,
            "file_name": file_name,
        })

    def _chat_history_to_markdown(self, chat_history):
        """将聊天记录转换为 Markdown"""
        md = ""
        cleaned_history = []

        for item in chat_history:
            question = item.get("question", "").strip()
            if (
                len(question) > 3
                and question.lower() not in ["你好", "hello", "hi", "test"]
                and not question.startswith("你好")
            ):
                cleaned_history.append(item)

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

    def _generate_summary(self, md_content):
        """使用 AI 生成报告摘要"""
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        if not api_key:
            return "AI 摘要生成失败：API Key 未配置"

        summary_prompt = (
            "你是一名专业金融分析师。请基于以下对话内容和资金流数据，直接生成一份完整、结构化、条理清晰、适合投资决策的最终资金流分析报告。"
            "报告必须包含：市场综述、资金流趋势、行业/板块表现、主力资金动向、风险提示、投资建议等。"
            "请直接输出最终Markdown正文，不要再嵌套任何markdown结构，也不要要求用户补充信息。"
            "\n\n" + md_content
        )

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一名专业金融分析师。"},
                {"role": "user", "content": summary_prompt},
            ],
            stream=False,
        )

        content = response.choices[0].message.content

        try:
            result = json.loads(content)
            return result.get("advice", content)
        except Exception:
            return content.strip()

    def _upload_to_minio(self, file_path, object_name):
        """上传文件到 MinIO"""
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        secret_key = os.getenv("MINIO_SECRET_KEY", "admin123")
        bucket = os.getenv("MINIO_BUCKET", "data-financial-agent")
        secure = os.getenv("MINIO_SECURE", "False").lower() in ["true", "1"]

        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

        # 确保 bucket 存在
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        # 上传文件
        file_stat = os.stat(file_path)
        with open(file_path, "rb") as f:
            client.put_object(
                bucket,
                object_name,
                f,
                file_stat.st_size,
                content_type="text/markdown",
            )

        # 生成预签名 URL
        url = client.presigned_get_object(
            bucket,
            object_name,
            expires=timedelta(days=1),
        )

        return url
