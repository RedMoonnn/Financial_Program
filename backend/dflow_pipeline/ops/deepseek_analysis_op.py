"""
DeepSeek AI 分析 OP - 分析金融数据生成报告
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dflow.python import OP, OPIO, OPIOSign, Artifact
from openai import OpenAI


def get_now():
    """获取北京时间"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


# 金融分析 Prompt 模板
ANALYSIS_PROMPT = """你是一名专业的金融分析师，擅长资金流分析和投资建议。请根据以下金融数据进行深度分析。

## 数据概览
- 数据类型: {data_type}
- 采集时间: {crawl_time}
- 数据条数: {data_count}

## 资金流数据
{data_summary}

## 分析要求
请从以下几个维度进行分析：

1. **市场整体趋势**：分析主力资金流向，判断市场多空氛围
2. **热点板块/个股**：找出资金净流入最多的板块或个股，分析原因
3. **风险提示**：识别资金大幅流出的领域，提醒潜在风险
4. **投资建议**：基于资金流数据，给出短期操作建议

请用专业但通俗易懂的语言作答，结构清晰，重点突出。
"""


class DeepSeekAnalysisOP(OP):
    """使用 DeepSeek 分析金融数据并生成报告"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "stock_data_file": Artifact(Path),  # 个股数据文件
                "sector_data_file": Artifact(Path),  # 板块数据文件
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "report_file": Artifact(Path),  # 分析报告 JSON 文件
                "summary": str,  # 简要摘要
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        stock_data_file = op_in["stock_data_file"]
        sector_data_file = op_in["sector_data_file"]

        # 读取数据
        with open(stock_data_file, "r", encoding="utf-8") as f:
            stock_data = json.load(f)

        with open(sector_data_file, "r", encoding="utf-8") as f:
            sector_data = json.load(f)

        # 生成数据摘要
        data_summary = self._generate_data_summary(stock_data, sector_data)

        # 统计数据
        stock_count = sum(len(item["data"]) for item in stock_data)
        sector_count = sum(len(item["data"]) for item in sector_data)
        total_count = stock_count + sector_count

        # 构建 Prompt
        prompt = ANALYSIS_PROMPT.format(
            data_type="个股资金流 + 板块资金流",
            crawl_time=get_now(),
            data_count=total_count,
            data_summary=data_summary,
        )

        # 调用 DeepSeek API
        analysis_result = self._call_deepseek(prompt)

        # 构建完整报告
        report = {
            "report_time": get_now(),
            "data_stats": {
                "stock_tables": len(stock_data),
                "sector_tables": len(sector_data),
                "stock_records": stock_count,
                "sector_records": sector_count,
            },
            "analysis": analysis_result,
            "raw_prompt": prompt,
        }

        # 保存报告
        output_path = Path("/tmp/financial_analysis_report.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 提取摘要
        summary = (
            analysis_result[:500]
            if isinstance(analysis_result, str)
            else str(analysis_result)[:500]
        )

        return OPIO(
            {
                "report_file": output_path,
                "summary": summary,
            }
        )

    def _generate_data_summary(self, stock_data, sector_data):
        """生成数据摘要供 AI 分析"""
        summary_parts = []

        # 个股数据摘要 - 取每个表的 Top 5 主力净流入
        summary_parts.append("### 个股资金流 Top 数据")
        for item in stock_data[:4]:  # 只取前 4 个表（减少 token）
            table_name = item["table_name"]
            data = item["data"]
            if not data:
                continue

            # 按主力净流入排序取 Top 5
            sorted_data = sorted(
                data, key=lambda x: x.get("main_flow_net_amount", 0), reverse=True
            )[:5]

            summary_parts.append(f"\n**{table_name}** (Top 5 主力净流入):")
            for d in sorted_data:
                summary_parts.append(
                    f"- {d['name']}({d['code']}): 主力净流入 {d.get('main_flow_net_amount', 0):.2f}万, "
                    f"涨跌幅 {d.get('change_percentage', 0):.2f}%"
                )

        # 板块数据摘要
        summary_parts.append("\n### 板块资金流 Top 数据")
        for item in sector_data:
            table_name = item["table_name"]
            data = item["data"]
            if not data:
                continue

            # 按主力净流入排序取 Top 5
            sorted_data = sorted(
                data, key=lambda x: x.get("main_flow_net_amount", 0), reverse=True
            )[:5]

            summary_parts.append(f"\n**{table_name}** (Top 5 主力净流入):")
            for d in sorted_data:
                summary_parts.append(
                    f"- {d['name']}({d['code']}): 主力净流入 {d.get('main_flow_net_amount', 0):.2f}万, "
                    f"涨跌幅 {d.get('change_percentage', 0):.2f}%"
                )

        return "\n".join(summary_parts)

    def _call_deepseek(self, prompt):
        """调用 DeepSeek API"""
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        if not api_key:
            return "错误：DEEPSEEK_API_KEY 未配置，请设置环境变量"

        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名资深金融分析师，擅长从资金流数据中洞察市场趋势，给出专业的投资建议。",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                max_tokens=2000,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"调用 DeepSeek API 失败: {str(e)}"
