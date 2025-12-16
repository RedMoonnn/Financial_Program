"""
数据采集 OP - 个股资金流和板块资金流采集
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dflow.python import OP, OPIO, OPIOSign, Artifact


# 东方财富 API 配置
BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# 市场配置
MARKET_NAMES = [
    "All_Stocks",
    "SH&SZ_A_Shares",
    "SH_A_Shares",
    "STAR_Market",
    "SZ_A_Shares",
    "ChiNext_Market",
    "SH_B_Shares",
    "SZ_B_Shares",
]

MARKET_IDS = [
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:23+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
    "m:0+t:80+f:!2",
    "m:1+t:3+f:!2",
    "m:0+t:7+f:!2",
]

# 板块配置
DETAIL_NAMES = ["Industry_Flow", "Concept_Flow", "Regional_Flow"]
DETAIL_IDS = ["m:90+t:2", "m:90+t:3", "m:90+t:1"]

# 周期配置
PERIODS = ["today", "3d", "5d", "10d"]
PERIOD_NAMES = ["Today", "3_Day", "5_Day", "10_Day"]
SECTOR_PERIODS = ["today", "5d", "10d"]
SECTOR_PERIOD_NAMES = ["Today", "5_Day", "10_Day"]

# 字段配置
FLOWS_ID = [
    "jquery112309245886249999282_1733396772298",
    "jQuery112309570655592067874_1733410054611",
]
DAY_IDS = ["f62", "f267", "f164", "f174"]
DAY2_IDS = ["f62", "f164", "f174"]
FIELDS_IDS = [
    "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
    "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
    "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
    "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
]


def get_now():
    """获取北京时间"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def safe_float(val):
    """安全转换为浮点数"""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def process_diff_today(diff):
    return {
        "latest_price": safe_float(diff.get("f2", 0)),
        "change_percentage": safe_float(diff.get("f3", 0)),
        "main_flow_net_amount": safe_float(diff.get("f62", 0)),
        "main_flow_net_percentage": safe_float(diff.get("f184", 0)),
        "extra_large_order_flow_net_amount": safe_float(diff.get("f66", 0)),
        "extra_large_order_flow_net_percentage": safe_float(diff.get("f69", 0)),
        "large_order_flow_net_amount": safe_float(diff.get("f72", 0)),
        "large_order_flow_net_percentage": safe_float(diff.get("f75", 0)),
        "medium_order_flow_net_amount": safe_float(diff.get("f78", 0)),
        "medium_order_flow_net_percentage": safe_float(diff.get("f81", 0)),
        "small_order_flow_net_amount": safe_float(diff.get("f84", 0)),
        "small_order_flow_net_percentage": safe_float(diff.get("f87", 0)),
    }


def process_diff_3d(diff):
    return {
        "latest_price": safe_float(diff.get("f2", 0)),
        "change_percentage": safe_float(diff.get("f127", 0)),
        "main_flow_net_amount": safe_float(diff.get("f267", 0)),
        "main_flow_net_percentage": safe_float(diff.get("f268", 0)),
        "extra_large_order_flow_net_amount": safe_float(diff.get("f269", 0)),
        "extra_large_order_flow_net_percentage": safe_float(diff.get("f270", 0)),
        "large_order_flow_net_amount": safe_float(diff.get("f271", 0)),
        "large_order_flow_net_percentage": safe_float(diff.get("f272", 0)),
        "medium_order_flow_net_amount": safe_float(diff.get("f273", 0)),
        "medium_order_flow_net_percentage": safe_float(diff.get("f274", 0)),
        "small_order_flow_net_amount": safe_float(diff.get("f275", 0)),
        "small_order_flow_net_percentage": safe_float(diff.get("f276", 0)),
    }


def process_diff_5d(diff):
    return {
        "latest_price": safe_float(diff.get("f2", 0)),
        "change_percentage": safe_float(diff.get("f109", 0)),
        "main_flow_net_amount": safe_float(diff.get("f164", 0)),
        "main_flow_net_percentage": safe_float(diff.get("f165", 0)),
        "extra_large_order_flow_net_amount": safe_float(diff.get("f166", 0)),
        "extra_large_order_flow_net_percentage": safe_float(diff.get("f167", 0)),
        "large_order_flow_net_amount": safe_float(diff.get("f168", 0)),
        "large_order_flow_net_percentage": safe_float(diff.get("f169", 0)),
        "medium_order_flow_net_amount": safe_float(diff.get("f170", 0)),
        "medium_order_flow_net_percentage": safe_float(diff.get("f171", 0)),
        "small_order_flow_net_amount": safe_float(diff.get("f172", 0)),
        "small_order_flow_net_percentage": safe_float(diff.get("f173", 0)),
    }


def process_diff_10d(diff):
    return {
        "latest_price": safe_float(diff.get("f2", 0)),
        "change_percentage": safe_float(diff.get("f160", 0)),
        "main_flow_net_amount": safe_float(diff.get("f174", 0)),
        "main_flow_net_percentage": safe_float(diff.get("f175", 0)),
        "extra_large_order_flow_net_amount": safe_float(diff.get("f176", 0)),
        "extra_large_order_flow_net_percentage": safe_float(diff.get("f177", 0)),
        "large_order_flow_net_amount": safe_float(diff.get("f178", 0)),
        "large_order_flow_net_percentage": safe_float(diff.get("f179", 0)),
        "medium_order_flow_net_amount": safe_float(diff.get("f180", 0)),
        "medium_order_flow_net_percentage": safe_float(diff.get("f181", 0)),
        "small_order_flow_net_amount": safe_float(diff.get("f182", 0)),
        "small_order_flow_net_percentage": safe_float(diff.get("f183", 0)),
    }


class CrawlStockFlowOP(OP):
    """个股资金流采集 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            "market_choice": int,  # 1-8
            "day_choice": int,     # 1-4
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            "data_file": Artifact(Path),
            "count": int,
            "table_name": str,
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        market_choice = op_in["market_choice"]
        day_choice = op_in["day_choice"]

        market_type = MARKET_NAMES[market_choice - 1]
        period = PERIODS[day_choice - 1]
        table_name = f"Stock_Flow_{market_type}_{PERIOD_NAMES[day_choice - 1]}"

        # 采集数据
        data = self._fetch_stock_data(market_choice, day_choice, market_type, period)

        # 保存为 JSON 文件
        output_path = Path(f"/tmp/stock_{market_choice}_{day_choice}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "table_name": table_name,
                "data": data,
            }, f, ensure_ascii=False)

        return OPIO({
            "data_file": output_path,
            "count": len(data),
            "table_name": table_name,
        })

    def _fetch_stock_data(self, market_choice, day_choice, market_type, period):
        """采集个股资金流数据"""
        cb = FLOWS_ID[0]
        fs = MARKET_IDS[market_choice - 1]
        fid = DAY_IDS[day_choice - 1]
        fields = FIELDS_IDS[day_choice - 1]

        params = {
            "cb": cb,
            "fid": fid,
            "pn": "1",
            "pz": 50,
            "fs": fs,
            "fields": fields,
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }

        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = response.text

        # 解析 JSONP 响应
        if data.strip().startswith("{"):
            parsed_data = json.loads(data)
        elif "(" in data and ")" in data:
            start_index = data.find("(") + 1
            end_index = data.rfind(")")
            json_str = data[start_index:end_index]
            parsed_data = json.loads(json_str)
        else:
            raise Exception(f"无法解析响应: {data[:200]}")

        data_field = parsed_data.get("data")
        if not data_field or not isinstance(data_field, dict):
            return []

        diff_list = data_field.get("diff", [])
        results = []

        for diff in diff_list:
            item = {
                "code": diff["f12"],
                "name": diff["f14"],
                "flow_type": "Stock_Flow",
                "market_type": market_type,
                "period": period,
                "crawl_time": get_now(),
            }

            # 根据周期选择处理函数
            if period == "today":
                item.update(process_diff_today(diff))
            elif period == "3d":
                item.update(process_diff_3d(diff))
            elif period == "5d":
                item.update(process_diff_5d(diff))
            elif period == "10d":
                item.update(process_diff_10d(diff))
            else:
                item.update(process_diff_today(diff))

            results.append(item)

        return results


class CrawlSectorFlowOP(OP):
    """板块资金流采集 OP"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            "detail_choice": int,  # 1-3
            "day_choice": int,     # 1-3
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            "data_file": Artifact(Path),
            "count": int,
            "table_name": str,
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        detail_choice = op_in["detail_choice"]
        day_choice = op_in["day_choice"]

        detail_type = DETAIL_NAMES[detail_choice - 1]
        period = SECTOR_PERIODS[day_choice - 1]
        table_name = f"Sector_Flow_{detail_type}_{SECTOR_PERIOD_NAMES[day_choice - 1]}"

        # 采集数据
        data = self._fetch_sector_data(detail_choice, day_choice, detail_type, period)

        # 保存为 JSON 文件
        output_path = Path(f"/tmp/sector_{detail_choice}_{day_choice}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "table_name": table_name,
                "data": data,
            }, f, ensure_ascii=False)

        return OPIO({
            "data_file": output_path,
            "count": len(data),
            "table_name": table_name,
        })

    def _fetch_sector_data(self, detail_choice, day_choice, detail_type, period):
        """采集板块资金流数据"""
        cb = FLOWS_ID[1]
        fs = DETAIL_IDS[detail_choice - 1]
        fid = DAY2_IDS[day_choice - 1]

        # 板块周期字段索引: today=0, 5d=2, 10d=3
        field_idx = [0, 2, 3][day_choice - 1]
        fields = FIELDS_IDS[field_idx]

        params = {
            "cb": cb,
            "fid": fid,
            "pn": "1",
            "pz": 50,
            "fs": fs,
            "fields": fields,
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }

        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = response.text

        # 解析 JSONP 响应
        if data.strip().startswith("{"):
            parsed_data = json.loads(data)
        elif "(" in data and ")" in data:
            start_index = data.find("(") + 1
            end_index = data.rfind(")")
            json_str = data[start_index:end_index]
            parsed_data = json.loads(json_str)
        else:
            raise Exception(f"无法解析响应: {data[:200]}")

        data_field = parsed_data.get("data")
        if not data_field or not isinstance(data_field, dict):
            return []

        diff_list = data_field.get("diff", [])
        results = []

        for diff in diff_list:
            item = {
                "code": diff["f12"],
                "name": diff["f14"],
                "flow_type": "Sector_Flow",
                "market_type": detail_type,
                "period": period,
                "crawl_time": get_now(),
            }

            # 根据周期选择处理函数
            if period == "today":
                item.update(process_diff_today(diff))
            elif period == "5d":
                item.update(process_diff_5d(diff))
            elif period == "10d":
                item.update(process_diff_10d(diff))
            else:
                item.update(process_diff_today(diff))

            results.append(item)

        return results
