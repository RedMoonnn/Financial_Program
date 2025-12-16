"""
AI 分析 OP - 使用 DeepSeek 进行资金流分析
"""

import os
import json
from pathlib import Path
from dflow.python import OP, OPIO, OPIOSign, Artifact
import pymysql
from openai import OpenAI


def get_db_config():
    """获取数据库配置"""
    return {
        "host": os.getenv("MYSQL_HOST", "mysql"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "charset": "utf8mb4",
    }


class AIAnalysisOP(OP):
    """AI 智能分析 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "table_name": str,
                "query": str,
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "analysis_result": Artifact(Path),
                "summary": str,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        table_name = op_in["table_name"]
        query = op_in["query"]

        # 从数据库获取数据
        flow_data = self._query_table_data(table_name, limit=50)

        if not flow_data:
            result = {
                "advice": "数据缺失",
                "reasons": [f"数据库中未找到表 {table_name} 或无数据"],
            }
        else:
            # 调用 DeepSeek 分析
            result = self._analyze_with_deepseek(flow_data, query)

        # 保存结果
        output_path = Path(f"/tmp/ai_analysis_{table_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        summary = result.get("advice", str(result))[:500]

        return OPIO(
            {
                "analysis_result": output_path,
                "summary": summary,
            }
        )

    def _query_table_data(self, table_name, limit=50):
        """从数据库查询数据"""
        db_config = get_db_config()
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            if not cursor.fetchone():
                return []

            cursor.execute(
                f"SELECT * FROM `{table_name}` ORDER BY crawl_time DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()

            # 转换为分析格式
            result = []
            parts = table_name.split("_")
            flow_type = f"{parts[0]}_{parts[1]}"
            market_type = "_".join(parts[2:-1])
            period = parts[-1]

            for row in rows:
                result.append(
                    {
                        "type": "stock" if flow_type == "Stock_Flow" else "sector",
                        "flow_type": flow_type,
                        "market_type": market_type,
                        "period": period,
                        "data": {
                            "code": row.get("code"),
                            "name": row.get("name"),
                            "main_flow_net_amount": row.get("main_flow_net_amount"),
                            "main_flow_net_percentage": row.get(
                                "main_flow_net_percentage"
                            ),
                            "change_percentage": row.get("change_percentage"),
                            "crawl_time": str(row.get("crawl_time")),
                        },
                    }
                )

            return result

        finally:
            cursor.close()
            conn.close()

    def _analyze_with_deepseek(self, flow_data, query):
        """使用 DeepSeek 进行分析"""
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        if not api_key:
            return {
                "advice": "API Key 未配置",
                "reasons": ["请设置 DEEPSEEK_API_KEY 环境变量"],
            }

        # 构建 prompt
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
                    "main_flow_net_percentage": d["data"]["main_flow_net_percentage"],
                    "change_percentage": d["data"]["change_percentage"],
                    "crawl_time": d["data"]["crawl_time"],
                },
            }
            for d in flow_data
        ]

        prompt = f"""
你是一名专业金融智能顾问，请结合下方资金流数据，用自然、通俗的语言为用户分析并给出建议。

【资金流数据】
{json.dumps(slim_data, ensure_ascii=False, indent=2)}

【用户问题】
{query}

请用专业风格作答。
"""

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名专业金融分析师，善于资金流分析和投资建议。",
                },
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )

        content = response.choices[0].message.content

        # 尝试解析 JSON
        try:
            return json.loads(content)
        except Exception:
            import re

            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            return {"advice": content.strip()}
