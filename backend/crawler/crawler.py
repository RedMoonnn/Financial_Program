import requests
from program.utils.utils import get_now

# 东方财富API参数配置（可根据实际需求扩展）
BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# 字段映射（以今日排行为例，其他周期可扩展）
FIELD_MAP = {
    'today': {
        'change': 'f3',
        'main': 'f62', 'main_pct': 'f184',
        'xl': 'f66', 'xl_pct': 'f69',
        'l': 'f72', 'l_pct': 'f75',
        'm': 'f78', 'm_pct': 'f81',
        's': 'f84', 's_pct': 'f87',
    },
    # 可扩展3d/5d/10d等
}

# 采集函数，返回结构化数据列表
def fetch_flow_data(flow_type, market_type, period, pages=1):
    results = []
    for page in range(1, int(pages)+1):
        params = {
            # 这里应根据实际API参数动态生成
            "pn": page,
            "pz": 50,
            # ... 其他参数 ...
        }
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = response.text
        # 解析JSONP
        start_index = data.find('(') + 1
        end_index = data.rfind(')')
        json_str = data[start_index:end_index]
        parsed_data = requests.utils.json.loads(json_str)
        diff_list = parsed_data['data']['diff']
        for diff in diff_list:
            item = {
                'code': diff['f12'],
                'name': diff['f14'],
                'flow_type': flow_type,
                'market_type': market_type,
                'period': period,
                'latest_price': float(diff.get('f2', 0)),
                'change_percentage': float(diff.get(FIELD_MAP[period]['change'], 0)),
                'main_flow_net_amount': float(diff.get(FIELD_MAP[period]['main'], 0)),
                'main_flow_net_percentage': float(diff.get(FIELD_MAP[period]['main_pct'], 0)),
                'extra_large_order_flow_net_amount': float(diff.get(FIELD_MAP[period]['xl'], 0)),
                'extra_large_order_flow_net_percentage': float(diff.get(FIELD_MAP[period]['xl_pct'], 0)),
                'large_order_flow_net_amount': float(diff.get(FIELD_MAP[period]['l'], 0)),
                'large_order_flow_net_percentage': float(diff.get(FIELD_MAP[period]['l_pct'], 0)),
                'medium_order_flow_net_amount': float(diff.get(FIELD_MAP[period]['m'], 0)),
                'medium_order_flow_net_percentage': float(diff.get(FIELD_MAP[period]['m_pct'], 0)),
                'small_order_flow_net_amount': float(diff.get(FIELD_MAP[period]['s'], 0)),
                'small_order_flow_net_percentage': float(diff.get(FIELD_MAP[period]['s_pct'], 0)),
                'crawl_time': get_now(),
            }
            results.append(item)
    return results 