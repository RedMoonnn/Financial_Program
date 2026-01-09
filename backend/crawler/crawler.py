import json
import sys
from datetime import datetime, timedelta, timezone

import pymysql
import requests

# 东方财富API参数配置
BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

FIELD_MAP = {
    "today": {
        "change": "f3",
        "main": "f62",
        "main_pct": "f184",
        "xl": "f66",
        "xl_pct": "f69",
        "l": "f72",
        "l_pct": "f75",
        "m": "f78",
        "m_pct": "f81",
        "s": "f84",
        "s_pct": "f87",
    },
    "3d": {
        "change": "f4",
        "main": "f65",
        "main_pct": "f185",
        "xl": "f67",
        "xl_pct": "f70",
        "l": "f73",
        "l_pct": "f76",
        "m": "f79",
        "m_pct": "f82",
        "s": "f85",
        "s_pct": "f88",
    },
    "5d": {
        "change": "f5",
        "main": "f68",
        "main_pct": "f186",
        "xl": "f71",
        "xl_pct": "f74",
        "l": "f77",
        "l_pct": "f80",
        "m": "f83",
        "m_pct": "f86",
        "s": "f89",
        "s_pct": "f90",
    },
    "10d": {
        "change": "f6",
        "main": "f91",
        "main_pct": "f92",
        "xl": "f93",
        "xl_pct": "f94",
        "l": "f95",
        "l_pct": "f96",
        "m": "f97",
        "m_pct": "f98",
        "s": "f99",
        "s_pct": "f100",
    },
}


def get_now():
    # 强制东八区北京时间
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


# ====== 参数组合迁移自 test_crawler/source_data_1.py ======
flows_id = [
    "jquery112309245886249999282_1733396772298",
    "jQuery112309570655592067874_1733410054611",
]
flows_names = ["Stock_Flow", "Sector_Flow"]
market_ids = [
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:2+f:!2,m:1+t:23+f:!2",
    "m:1+t:23+f:!2",
    "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
    "m:0+t:80+f:!2",
    "m:1+t:3+f:!2",
    "m:0+t:7+f:!2",
]
market_names = [
    "All_Stocks",
    "SH&SZ_A_Shares",
    "SH_A_Shares",
    "STAR_Market",
    "SZ_A_Shares",
    "ChiNext_Market",
    "SH_B_Shares",
    "SZ_B_Shares",
]
detail_flows_ids = ["m:90+t:2", "m:90+t:3", "m:90+t:1"]
detail_flows_names = ["Industry_Flow", "Concept_Flow", "Regional_Flow"]
day1_ids = ["f62", "f267", "f164", "f174"]
day1_names = ["Today_Ranking", "3_Day_Ranking", "5_Day_Ranking", "10_Day_Ranking"]
day2_ids = ["f62", "f164", "f174"]
day2_names = ["Today_Ranking", "5_Day_Ranking", "10_Day_Ranking"]
fields_ids = [
    "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
    "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
    "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
    "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
]


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# === 资金流数据清洗函数（对齐 test_crawler/source_data_1.py） ===
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


# 采集函数，返回结构化数据列表
def fetch_flow_data(
    flow_type,
    market_type,
    period,
    pages=1,
    flow_choice=None,
    market_choice=None,
    detail_choice=None,
    day_choice=None,
):
    # 参数校验
    if flow_type == "Stock_Flow":
        if market_choice is None or not (1 <= market_choice <= 8):
            raise ValueError("Stock_Flow 采集时，market_choice 必须为 1~8，且不能为None")
    elif flow_type == "Sector_Flow":
        if detail_choice is None or not (1 <= detail_choice <= 3):
            raise ValueError("Sector_Flow 采集时，detail_choice 必须为 1~3，且不能为None")
    else:
        raise ValueError("flow_type 必须为 'Stock_Flow' 或 'Sector_Flow'")
    results = []
    for page in range(1, int(pages) + 1):
        # 动态参数组合
        if flow_type == "Stock_Flow":
            cb = flows_id[0]
            fs = market_ids[market_choice - 1]
            if period == "today":
                fid = day1_ids[0]
                fields = fields_ids[0]
            elif period == "3d":
                fid = day1_ids[1]
                fields = fields_ids[1]
            elif period == "5d":
                fid = day1_ids[2]
                fields = fields_ids[2]
            elif period == "10d":
                fid = day1_ids[3]
                fields = fields_ids[3]
            else:
                fid = day1_ids[0]
                fields = fields_ids[0]
        else:  # Sector_Flow
            cb = flows_id[1]
            fs = detail_flows_ids[detail_choice - 1]
            if period == "today":
                fid = day2_ids[0]
                fields = fields_ids[0]
            elif period == "5d":
                fid = day2_ids[1]
                fields = fields_ids[2]
            elif period == "10d":
                fid = day2_ids[2]
                fields = fields_ids[3]
            else:
                fid = day2_ids[0]
                fields = fields_ids[0]
        # 新增日志打印
        # print(f"[采集日志] 正在爬取: flow_type={flow_type}, market_type={market_type}, period={period}, page={page}")
        params = {
            "cb": cb,
            "fid": fid,
            "pn": str(page),
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
        try:
            if data.strip().startswith("{"):
                parsed_data = json.loads(data)
            elif "(" in data and ")" in data:
                start_index = data.find("(") + 1
                end_index = data.rfind(")")
                json_str = data[start_index:end_index]
                parsed_data = json.loads(json_str)
            else:
                raise Exception(f"返回内容无法解析为JSON: {data[:200]}")
        except Exception as e:
            print(f"解析东方财富返回内容失败: {e}")
            print(f"返回内容: {data[:200]}")
            raise
        data_field = parsed_data.get("data")
        if not data_field or not isinstance(data_field, dict):
            print(f"采集无数据或接口异常，返回内容: {data[:200]}")
            return []
        diff_list = data_field.get("diff", [])
        for diff in diff_list:
            item = {
                "code": diff["f12"],
                "name": diff["f14"],
                "flow_type": flow_type,
                "market_type": market_type,
                "period": period,
                "crawl_time": get_now(),
            }
            # 分发清洗逻辑
            if period == "today":
                item.update(process_diff_today(diff))
            elif period == "3d":
                item.update(process_diff_3d(diff))
            elif period == "5d":
                item.update(process_diff_5d(diff))
            elif period == "10d":
                item.update(process_diff_10d(diff))
            else:
                # 默认today
                item.update(process_diff_today(diff))
            results.append(item)
    return results


def get_db_config():
    """
    获取数据库配置
    统一使用core.config中的配置，但保留此函数以兼容现有代码
    注意：爬虫模块使用PyMySQL直接连接，因为需要动态创建表
    """
    from core.config import database_settings

    config = database_settings.config_dict
    # 爬虫默认使用mysql作为host（Docker环境），如果配置为localhost则使用mysql
    if config["host"] == "localhost":
        config["host"] = "mysql"  # Docker环境下的服务名
    return config


def store_data_to_db(data, table_name):
    if not data:
        return
    db_config = get_db_config()
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            `Index` INT PRIMARY KEY AUTO_INCREMENT,
            `code` VARCHAR(10),
            `name` VARCHAR(50),
            `flow_type` VARCHAR(32),
            `market_type` VARCHAR(32),
            `period` VARCHAR(16),
            `latest_price` FLOAT,
            `change_percentage` FLOAT,
            `main_flow_net_amount` FLOAT,
            `main_flow_net_percentage` FLOAT,
            `extra_large_order_flow_net_amount` FLOAT,
            `extra_large_order_flow_net_percentage` FLOAT,
            `large_order_flow_net_amount` FLOAT,
            `large_order_flow_net_percentage` FLOAT,
            `medium_order_flow_net_amount` FLOAT,
            `medium_order_flow_net_percentage` FLOAT,
            `small_order_flow_net_amount` FLOAT,
            `small_order_flow_net_percentage` FLOAT,
            `crawl_time` DATETIME
        ) DEFAULT CHARSET=utf8mb4;
    """)
    # 新增：每次采集前清空表
    cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
    for record in data:
        cursor.execute(
            f"""
            INSERT INTO `{table_name}` (
                `code`, `name`, `flow_type`, `market_type`, `period`, `latest_price`,
                `change_percentage`, `main_flow_net_amount`, `main_flow_net_percentage`,
                `extra_large_order_flow_net_amount`, `extra_large_order_flow_net_percentage`,
                `large_order_flow_net_amount`, `large_order_flow_net_percentage`,
                `medium_order_flow_net_amount`, `medium_order_flow_net_percentage`,
                `small_order_flow_net_amount`, `small_order_flow_net_percentage`,
                `crawl_time`
            ) VALUES (
                %(code)s, %(name)s, %(flow_type)s, %(market_type)s, %(period)s, %(latest_price)s,
                %(change_percentage)s, %(main_flow_net_amount)s, %(main_flow_net_percentage)s,
                %(extra_large_order_flow_net_amount)s, %(extra_large_order_flow_net_percentage)s,
                %(large_order_flow_net_amount)s, %(large_order_flow_net_percentage)s,
                %(medium_order_flow_net_amount)s, %(medium_order_flow_net_percentage)s,
                %(small_order_flow_net_amount)s, %(small_order_flow_net_percentage)s,
                %(crawl_time)s
            )
            ON DUPLICATE KEY UPDATE
                `latest_price`=VALUES(`latest_price`),
                `change_percentage`=VALUES(`change_percentage`),
                `main_flow_net_amount`=VALUES(`main_flow_net_amount`),
                `main_flow_net_percentage`=VALUES(`main_flow_net_percentage`),
                `extra_large_order_flow_net_amount`=VALUES(`extra_large_order_flow_net_amount`),
                `extra_large_order_flow_net_percentage`=VALUES(`extra_large_order_flow_net_percentage`),
                `large_order_flow_net_amount`=VALUES(`large_order_flow_net_amount`),
                `large_order_flow_net_percentage`=VALUES(`large_order_flow_net_percentage`),
                `medium_order_flow_net_amount`=VALUES(`medium_order_flow_net_amount`),
                `medium_order_flow_net_percentage`=VALUES(`medium_order_flow_net_percentage`),
                `small_order_flow_net_amount`=VALUES(`small_order_flow_net_amount`),
                `small_order_flow_net_percentage`=VALUES(`small_order_flow_net_percentage`),
                `crawl_time`=VALUES(`crawl_time`)
        """,
            record,
        )
    conn.commit()
    cursor.close()
    conn.close()


def run_collect(flow_choice, market_choice, detail_choice, day_choice, pages):
    # 采集单个组合
    if flow_choice == 1:
        flow_type = "Stock_Flow"
        market_names = [
            "All_Stocks",
            "SH&SZ_A_Shares",
            "SH_A_Shares",
            "STAR_Market",
            "SZ_A_Shares",
            "ChiNext_Market",
            "SH_B_Shares",
            "SZ_B_Shares",
        ]
        market_type = market_names[market_choice - 1]
        period = ["today", "3d", "5d", "10d"][day_choice - 1]
        table_name = (
            f"Stock_Flow_{market_type}_{['Today', '3_Day', '5_Day', '10_Day'][day_choice - 1]}"
        )
        data = fetch_flow_data(
            flow_type,
            market_type,
            period,
            pages,
            flow_choice=flow_choice,
            market_choice=market_choice,
            detail_choice=detail_choice,
            day_choice=day_choice,
        )
    elif flow_choice == 2:
        flow_type = "Sector_Flow"
        detail_flows_names = ["Industry_Flow", "Concept_Flow", "Regional_Flow"]
        market_type = detail_flows_names[detail_choice - 1]
        period = ["today", "5d", "10d"][day_choice - 1]
        table_name = f"Sector_Flow_{market_type}_{['Today', '5_Day', '10_Day'][day_choice - 1]}"
        data = fetch_flow_data(
            flow_type,
            market_type,
            period,
            pages,
            flow_choice=flow_choice,
            market_choice=market_choice,
            detail_choice=detail_choice,
            day_choice=day_choice,
        )
    else:
        return {"error": "参数错误"}
    store_data_to_db(data, table_name)
    return {
        "table": table_name,
        "count": len(data),
        "crawl_time": get_now(),
        "data": data,  # 新增：返回采集到的全部数据
    }


def run_collect_all():
    total = 0
    for flow_choice in [1, 2]:
        if flow_choice == 1:
            for market_choice in range(1, 9):
                for day_choice in range(1, 5):
                    res = run_collect(flow_choice, market_choice, None, day_choice, 1)
                    total += res["count"]
        else:
            for detail_choice in range(1, 4):
                for day_choice in range(1, 4):
                    res = run_collect(flow_choice, None, detail_choice, day_choice, 1)
                    total += res["count"]
    return {"msg": "全量采集完成", "total": total, "crawl_time": get_now()}


def start_crawler_job():
    print("start_crawler_job called", file=sys.stderr, flush=True)
    from apscheduler.schedulers.background import BackgroundScheduler
    from services.common.cache_service import set_data_ready

    # 全局计数器
    start_crawler_job.crawl_count = 0

    def crawl_and_save():
        print("crawl_and_save called", file=sys.stderr, flush=True)
        try:
            set_data_ready(False)
            # 个股资金流 Stock_Flow
            for market_choice in range(1, 9):
                for day_choice in range(1, 5):
                    flow_choice = 1
                    detail_choice = None
                    pages = 1
                    res = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
                    print(
                        f"Stock_Flow | 市场: {market_names[market_choice - 1]} | 周期: {['today', '3d', '5d', '10d'][day_choice - 1]} | 采集条数: {res['count']}",
                        file=sys.stderr,
                        flush=True,
                    )
            # 板块资金流 Sector_Flow
            for detail_choice in range(1, 4):
                for day_choice in range(1, 4):
                    flow_choice = 2
                    market_choice = None
                    pages = 1
                    res = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
                    print(
                        f"Sector_Flow | 板块: {detail_flows_names[detail_choice - 1]} | 周期: {['today', '5d', '10d'][day_choice - 1]} | 采集条数: {res['count']}",
                        file=sys.stderr,
                        flush=True,
                    )
            set_data_ready(True)
            # 采集次数+1
            start_crawler_job.crawl_count += 1
            print(
                f"全量数据采集完成，本进程累计采集次数：{start_crawler_job.crawl_count}",
                file=sys.stderr,
                flush=True,
            )
        except Exception as e:
            import traceback

            print("采集线程异常:", e, file=sys.stderr, flush=True)
            traceback.print_exc()

    # 启动时先全量采集一次
    crawl_and_save()

    # 定时增量刷新
    def refresh_job():
        crawl_and_save()

    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_job, "interval", minutes=5)
    scheduler.start()
    print("爬虫定时任务已启动，每5分钟自动刷新数据", file=sys.stderr, flush=True)


if __name__ == "__main__":
    import pprint

    # 测试采集个股资金流
    data = fetch_flow_data(
        "Stock_Flow",
        "All_Stocks",
        "today",
        1,
        flow_choice=1,
        market_choice=1,
        day_choice=1,
    )
    print(f"采集到{len(data)}条数据")
    for item in data[:2]:
        pprint.pprint(item)
    # 测试采集板块资金流
    data2 = fetch_flow_data(
        "Sector_Flow",
        "Industry_Flow",
        "today",
        1,
        flow_choice=2,
        detail_choice=1,
        day_choice=1,
    )
    print(f"采集到{len(data2)}条数据")
    for item in data2[:2]:
        pprint.pprint(item)
