import requests
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com') + '/v1/finance/advice'  # 假设API路径

# 封装Deepseek API调用

def get_investment_advice(flow_type, market_type, period, code, flow_data, user_message, history=None):
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'flow_type': flow_type,
        'market_type': market_type,
        'period': period,
        'code': code,
        'flow_data': flow_data,
        'user_message': user_message,
        'history': history or []
    }
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get('advice', '未能获取AI建议')

class DeepseekAgent:
    @staticmethod
    def build_prompt(flow_data, sector_data=None, style="专业", user_message=None, history=None):
        """
        生成结构化分析prompt，内置资金流分析规则，支持个性化风格和多轮追问。
        """
        rules = (
            "判断主力态度：主力净流入为正且占比高→主力资金在积极做多；主力净流出为负且占比高→主力资金在减仓、撤退。\n"
            "看超大单异动：超大单流入明显上涨→机构资金抄底/追涨；超大单流出剧烈→机构止盈、跑路信号。\n"
            "看散户情绪：小单净流入大增→散户盲目跟风追涨（高风险）；小单净流出→散户恐慌割肉（低吸机会）。\n"
            "配合板块资金流：看板块是否整体资金净流入，个股是否跟随。个股+板块双流入→更稳健的短线机会；个股流入但板块流出→孤立异动，需小心。"
        )
        prompt = f"""
你是一名专业的金融分析师，请根据以下资金流数据，结合如下分析规则，输出结构化投资建议：
分析规则：\n{rules}

个股资金流数据：{flow_data}
"""
        if sector_data:
            prompt += f"\n板块资金流数据：{sector_data}\n"
        if user_message:
            prompt += f"\n用户追问：{user_message}\n"
        prompt += f"\n请用{style}风格，输出如下结构化JSON：\n"
        prompt += (
            '{\n'
            '  "advice": "投资建议（如买入/观望/卖出）",\n'
            '  "reasons": ["主要理由1", "主要理由2"],\n'
            '  "risks": ["风险点1", "风险点2"],\n'
            '  "detail": "详细分析文本"\n'
            '}'
        )
        if history:
            prompt += f"\n历史对话：{history}"
        return prompt

    @staticmethod
    def analyze(flow_data, sector_data=None, style="专业", user_message=None, history=None):
        prompt = DeepseekAgent.build_prompt(flow_data, sector_data, style, user_message, history)
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-finance',
            'messages': [
                {"role": "system", "content": "你是一名专业金融分析师，善于资金流分析和投资建议。"},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        # 解析结构化JSON
        try:
            return response.json()['choices'][0]['message']['content']
        except Exception:
            return response.text 