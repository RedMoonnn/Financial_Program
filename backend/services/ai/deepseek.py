import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


class DeepseekAgent:
    @staticmethod
    def clean_history(history, max_items=5):
        """
        清理历史对话，只保留最近的几条有效对话
        """
        if not history:
            return None

        # 如果是字符串，尝试解析为列表
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except (json.JSONDecodeError, ValueError):
                return None

        # 过滤掉无效对话（如只有"你好"的简单对话）
        valid_history = []
        for item in history:
            if isinstance(item, dict):
                question = item.get("question", "").strip()

                # 过滤掉过于简单的对话
                if (
                    len(question) > 3
                    and question.lower() not in ["你好", "hello", "hi", "test"]
                    and not question.startswith("你好")
                ):
                    valid_history.append(item)

        # 只保留最近的几条对话
        return valid_history[-max_items:] if valid_history else None

    @staticmethod
    def build_prompt(flow_data, user_message, history=None, style="专业"):
        """
        优化的prompt构建：限制历史对话长度，避免token溢出
        """
        # 清理历史对话
        cleaned_history = DeepseekAgent.clean_history(history)

        prompt = f"""
你是一名专业金融智能顾问，请结合下方资金流数据，用自然、通俗的语言为用户分析并给出建议。
如数据不足，请温和提示用户补充信息。

【资金流数据】
{json.dumps(flow_data, ensure_ascii=False, indent=2)}

【用户问题】
{user_message}
"""

        # 只添加清理后的历史对话
        if cleaned_history:
            # 只保留关键信息，减少token消耗
            history_summary = []
            for item in cleaned_history:
                q = (
                    item.get("question", "")[:50] + "..."
                    if len(item.get("question", "")) > 50
                    else item.get("question", "")
                )
                a = item.get("answer", "")
                if isinstance(a, dict):
                    a = a.get("advice", str(a))[:100] + "..." if len(str(a)) > 100 else str(a)
                history_summary.append(f"Q: {q} | A: {a}")

            prompt += "\n【最近对话】\n" + "\n".join(history_summary)

        prompt += f"\n请用{style}风格作答。"
        # 检查prompt长度，如果过长则截断
        if len(prompt) > 8000:  # 设置合理的长度限制
            print(
                f"Warning: Prompt too long ({len(prompt)} chars), truncating...",
                flush=True,
            )
            prompt = prompt[:8000] + "\n\n[提示：对话历史过长，已截断]"
        return prompt

    @staticmethod
    def analyze(flow_data, user_message=None, history=None, style="专业"):
        prompt = DeepseekAgent.build_prompt(flow_data, user_message, history, style)

        request_payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业金融分析师，善于资金流分析和投资建议。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        print(
            "\n===== Deepseek Request Payload =====\n"
            + json.dumps(request_payload, ensure_ascii=False, indent=2)
            + "\n===============================\n",
            flush=True,
        )
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(**request_payload)
        print(
            "\n===== Deepseek Response Object =====\n"
            + str(response)
            + "\n===============================\n",
            flush=True,
        )
        content = response.choices[0].message.content
        # 自动清洗和提取标准JSON
        try:
            return json.loads(content)
        except Exception:
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            # 新增：如果content为自然语言，直接返回advice字段
            return {"advice": content.strip()}

    @staticmethod
    def analyze_stream(flow_data, user_message=None, history=None, style="专业"):
        """
        流式分析，支持区分 Thinking 和 text
        返回一个生成器，每次 yield 一个包含 type 和 content 的字典
        type 可以是 'thinking' 或 'text'
        """
        prompt = DeepseekAgent.build_prompt(flow_data, user_message, history, style)

        request_payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业金融分析师，善于资金流分析和投资建议。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": True,
        }

        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        try:
            stream = client.chat.completions.create(**request_payload)

            for chunk in stream:
                if not chunk.choices or len(chunk.choices) == 0:
                    continue

                delta = chunk.choices[0].delta
                if not delta:
                    continue

                # 检查是否有 thinking 内容（Deepseek 可能在不同字段中）
                # 尝试多种可能的字段名
                thinking_content = None
                if hasattr(delta, "thinking"):
                    thinking_content = getattr(delta, "thinking", None)
                elif hasattr(delta, "reasoning"):
                    thinking_content = getattr(delta, "reasoning", None)
                elif isinstance(delta, dict) and "thinking" in delta:
                    thinking_content = delta.get("thinking")

                if thinking_content:
                    yield {"type": "thinking", "content": thinking_content}

                # 检查是否有 text 内容
                text_content = None
                if hasattr(delta, "content"):
                    text_content = getattr(delta, "content", None)
                elif isinstance(delta, dict) and "content" in delta:
                    text_content = delta.get("content")

                if text_content:
                    yield {"type": "text", "content": text_content}

        except Exception as e:
            import traceback

            error_detail = traceback.format_exc()
            print(f"Stream error: {e}\n{error_detail}", flush=True)
            yield {"type": "error", "content": f"流式输出错误: {str(e)}"}


if __name__ == "__main__":
    # 构造测试数据
    flow_data = [
        {
            "type": "stock",
            "flow_type": "Stock_Flow",
            "market_type": "All_Stocks",
            "period": "today",
            "data": {
                "code": "600000",
                "name": "浦发银行",
                "latest_price": 10.5,
                "change_percentage": 1.2,
                "main_flow_net_amount": 1000000,
                "main_flow_net_percentage": 5.6,
                "extra_large_order_flow_net_amount": 500000,
                "extra_large_order_flow_net_percentage": 2.8,
                "large_order_flow_net_amount": 200000,
                "large_order_flow_net_percentage": 1.1,
                "medium_order_flow_net_amount": 150000,
                "medium_order_flow_net_percentage": 0.8,
                "small_order_flow_net_amount": 150000,
                "small_order_flow_net_percentage": 0.9,
                "crawl_time": "2024-05-01 10:00:00",
            },
        }
    ]
    user_message = "请帮我分析一下浦发银行今日的资金流情况"
    print("\n=== 本地测试AI对话 ===\n")
    result = DeepseekAgent.analyze(flow_data, user_message=user_message, history=None, style="专业")
