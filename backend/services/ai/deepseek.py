import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 从配置中获取DeepSeek参数设置
try:
    from core.config import deepseek_settings

    DEFAULT_MAX_TOKENS = deepseek_settings.max_tokens
    DEFAULT_TEMPERATURE = deepseek_settings.temperature
    DEFAULT_TOP_P = deepseek_settings.top_p
    DEFAULT_FREQUENCY_PENALTY = deepseek_settings.frequency_penalty
    DEFAULT_PRESENCE_PENALTY = deepseek_settings.presence_penalty
except ImportError:
    # 如果配置模块不可用，使用默认值
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 0.95
    DEFAULT_FREQUENCY_PENALTY = 0.0
    DEFAULT_PRESENCE_PENALTY = 0.0


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

        # 过滤掉无效对话
        valid_history = []
        for i, item in enumerate(history):
            if isinstance(item, dict):
                question = item.get("question", "").strip()
                # 保留最后一条消息，即使是简单的问候
                is_last = i == len(history) - 1

                # 过滤条件
                if len(question) > 1 or is_last:
                    valid_history.append(item)

        # 只保留最近的几条对话
        return valid_history[-max_items:] if valid_history else None

    @staticmethod
    def build_prompt(flow_data, user_message, history=None, style="专业"):
        """
        优化的prompt构建：优先回答用户的具体问题，然后结合资金流数据给出分析
        """
        # 清理历史对话
        cleaned_history = DeepseekAgent.clean_history(history)

        # 构建数据部分 - 仅在有数据时添加
        data_section = ""
        if flow_data:
            data_str = json.dumps(flow_data, ensure_ascii=False, indent=2)
            data_section = f"""
### 📊 相关资金流数据
以下数据仅作为回答的参考依据，请根据用户问题判断是否需要使用：
```json
{data_str}
```
"""

        # 优化后的 prompt 结构：采用结构化提示词
        prompt = f"""
### 🎯 用户核心问题
{user_message}

{data_section}

### 📝 回答原则
1. **优先响应问题**：直接针对用户的核心问题进行回答，不要顾左右而言他。
2. **数据驱动分析**：
   - 如果用户问题涉及具体的股票/板块，且上方【相关资金流数据】中有对应数据，请务必结合数据（如主力净流入、超大单占比等）进行量化分析。
   - 如果数据与问题无关（例如用户问"什么是股票"），请忽略数据，仅利用你的专业知识回答。
3. **输出风格**：
   - 请使用**{style}**风格。
   - 语言简练，逻辑清晰，关键结论可以加粗。
   - 避免堆砌过于晦涩的术语，必要时进行解释。
"""

        # 添加历史对话上下文
        if cleaned_history:
            # 只保留关键信息，减少token消耗
            history_summary = []
            for item in cleaned_history:
                q = (
                    item.get("question", "")[:100] + "..."
                    if len(item.get("question", "")) > 100
                    else item.get("question", "")
                )
                a = item.get("answer", "")
                # 处理 answer 可能是 dict 的情况
                if isinstance(a, dict):
                    advice = a.get("text") or a.get("advice") or str(a)
                    a_text = str(advice)[:200]
                else:
                    a_text = str(a)[:200]

                history_summary.append(f"User: {q}\nAssistant: {a_text}...")

            prompt += "\n### 🕒 最近对话上下文\n" + "\n".join(history_summary)

        # 检查prompt长度限制（基于token估算，1 token ≈ 4字符，64k tokens ≈ 256k字符）
        # 但为了安全起见，设置一个合理的字符限制（约50k字符，对应约12.5k tokens的输入）
        max_prompt_chars = 50000
        if len(prompt) > max_prompt_chars:
            print(
                f"Warning: Prompt too long ({len(prompt)} chars), truncating to {max_prompt_chars} chars...",
                flush=True,
            )
            prompt = prompt[:max_prompt_chars] + "\n\n[提示：由于上下文过长，部分内容已截断]"
        return prompt

    @staticmethod
    def chat(
        user_message,
        system_message=None,
        stream=False,
        max_tokens=None,
        temperature=None,
        top_p=None,
        frequency_penalty=None,
        presence_penalty=None,
    ):
        """
        使用 deepseek-chat 模型进行快速对话（非推理模型，速度更快）
        适用于报告生成等不需要推理过程的场景

        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            stream: 是否使用流式输出
            max_tokens: 最大输出token数（默认8192，最大支持8192）
            temperature: 温度参数，控制输出的随机性（0-2，越高越随机，默认0.7）
            top_p: 核采样参数，控制采样的多样性（0-1，默认0.95）
            frequency_penalty: 频率惩罚，减少重复内容（-2到2，默认0.0）
            presence_penalty: 存在惩罚，鼓励新话题（-2到2，默认0.0）

        Returns:
            如果 stream=False: 返回完整文本字符串
            如果 stream=True: 返回生成器，每次yield文本内容
        """
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})

        # 使用配置的默认值或传入的参数
        if max_tokens is None:
            max_tokens = DEFAULT_MAX_TOKENS
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE
        if top_p is None:
            top_p = DEFAULT_TOP_P
        if frequency_penalty is None:
            frequency_penalty = DEFAULT_FREQUENCY_PENALTY
        if presence_penalty is None:
            presence_penalty = DEFAULT_PRESENCE_PENALTY

        request_payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }

        try:
            if stream:
                # 定义内部生成器函数用于流式输出
                def stream_generator():
                    try:
                        response = client.chat.completions.create(**request_payload)
                        for chunk in response:
                            if not chunk.choices or len(chunk.choices) == 0:
                                continue
                            delta = chunk.choices[0].delta
                            if delta and hasattr(delta, "content") and delta.content:
                                yield delta.content
                    except Exception as e:
                        import traceback

                        error_detail = traceback.format_exc()
                        print(f"Chat stream error: {e}\n{error_detail}", flush=True)
                        yield f"AI服务调用失败: {str(e)}"

                return stream_generator()
            else:
                # 非流式输出，直接返回完整结果
                response = client.chat.completions.create(**request_payload)
                return response.choices[0].message.content
        except Exception as e:
            import traceback

            error_detail = traceback.format_exc()
            print(f"Chat error: {e}\n{error_detail}", flush=True)
            if stream:

                def error_gen(err=e):
                    yield f"AI服务调用失败: {str(err)}"

                return error_gen()
            else:
                return f"AI服务调用失败: {str(e)}"

    @staticmethod
    def analyze(
        flow_data,
        user_message=None,
        history=None,
        style="专业",
        max_tokens=None,
        temperature=None,
        top_p=None,
        frequency_penalty=None,
        presence_penalty=None,
    ):
        """
        非流式分析，直接返回完整结果
        使用 deepseek-reasoner 模型（推理模型，速度较慢但更准确）

        Args:
            flow_data: 资金流数据
            user_message: 用户消息
            history: 历史对话记录
            style: 输出风格
            max_tokens: 最大输出token数（默认8192，最大支持8192）
            temperature: 温度参数，控制输出的随机性（0-2，越高越随机，默认0.7）
            top_p: 核采样参数，控制采样的多样性（0-1，默认0.95）
            frequency_penalty: 频率惩罚，减少重复内容（-2到2，默认0.0）
            presence_penalty: 存在惩罚，鼓励新话题（-2到2，默认0.0）
        """
        full_text = ""
        full_thinking = ""

        # 复用 analyze_stream 获取结果
        try:
            stream = DeepseekAgent.analyze_stream(
                flow_data,
                user_message,
                history,
                style,
                max_tokens,
                temperature,
                top_p,
                frequency_penalty,
                presence_penalty,
            )

            for chunk in stream:
                if chunk["type"] == "text":
                    full_text += chunk["content"]
                elif chunk["type"] == "thinking":
                    full_thinking += chunk["content"]
                elif chunk["type"] == "error":
                    return {"advice": f"AI分析出错: {chunk['content']}", "thinking": full_thinking}

            return {"advice": full_text, "thinking": full_thinking}

        except Exception as e:
            return {"advice": f"AI服务调用失败: {str(e)}", "thinking": ""}

    @staticmethod
    def analyze_stream(
        flow_data,
        user_message=None,
        history=None,
        style="专业",
        max_tokens=None,
        temperature=None,
        top_p=None,
        frequency_penalty=None,
        presence_penalty=None,
    ):
        """
        流式分析，支持区分 Thinking 和 text
        返回一个生成器，每次 yield 一个包含 type 和 content 的字典
        type 可以是 'thinking' 或 'text'

        Args:
            flow_data: 资金流数据
            user_message: 用户消息
            history: 历史对话记录
            style: 输出风格
            max_tokens: 最大输出token数（默认8192，最大支持8192）
            temperature: 温度参数，控制输出的随机性（0-2，越高越随机，默认0.7）
            top_p: 核采样参数，控制采样的多样性（0-1，默认0.95）
            frequency_penalty: 频率惩罚，减少重复内容（-2到2，默认0.0）
            presence_penalty: 存在惩罚，鼓励新话题（-2到2，默认0.0）
        """
        prompt = DeepseekAgent.build_prompt(flow_data, user_message, history, style)

        # 使用配置的默认值或传入的参数
        if max_tokens is None:
            max_tokens = DEFAULT_MAX_TOKENS
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE
        if top_p is None:
            top_p = DEFAULT_TOP_P
        if frequency_penalty is None:
            frequency_penalty = DEFAULT_FREQUENCY_PENALTY
        if presence_penalty is None:
            presence_penalty = DEFAULT_PRESENCE_PENALTY

        request_payload = {
            "model": "deepseek-reasoner",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业金融分析师，善于资金流分析和投资建议。请优先直接回答用户的具体问题，然后结合数据给出详细分析。",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
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
                # DeepSeek API 返回 reasoning_content
                thinking_content = None
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    thinking_content = delta.reasoning_content
                elif hasattr(delta, "thinking") and delta.thinking:
                    thinking_content = delta.thinking
                elif hasattr(delta, "reasoning") and delta.reasoning:
                    thinking_content = delta.reasoning

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
    print("请使用 analyze_stream 进行流式分析测试")
