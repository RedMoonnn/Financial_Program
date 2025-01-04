# 保持热爱 奔赴山海

# 请求的基本URL和头部信息，用于访问API
url = "https://push2.eastmoney.com/api/qt/clist/get"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# 不同的流ID和名称，用于后续数据查询
flows_id = ["jquery112309245886249999282_1733396772298",
            "jQuery112309570655592067874_1733410054611"]

flows_names = ["Stock_Flow", "Sector_Flow"]  # ["个股资金流", "板块资金流"]

# 各个市场的ID和名称，用于指定查询的市场范围
market_ids = ["m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
              "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
              "m:1+t:2+f:!2,m:1+t:23+f:!2",
              "m:1+t:23+f:!2",
              "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
              "m:0+t:80+f:!2",
              "m:1+t:3+f:!2",
              "m:0+t:7+f:!2"]

market_names = ["All_Stocks",  # "全部股票"
                "SH&SZ_A_Shares",  # "沪深A股"
                "SH_A_Shares",  # "沪市A股"
                "STAR_Market",  # "科创板"
                "SZ_A_Shares",  # "深市A股"
                "ChiNext_Market",  # "创业板"
                "SH_B_Shares",  # "沪市B股"
                "SZ_B_Shares"]  # "深市B股

# 更详细的流ID和名称，指定不同的行业、概念、区域等流
detail_flows_ids = ["m:90+t:2", "m:90+t:3", "m:90+t:1"]
detail_flows_names = ["Industry_Flow", "Concept_Flow", "Regional_Flow"]  # ["行业资金流", "概念资金流", "地域资金流"]

# 不同日期区间的ID和名称，用于排名数据查询
day1_ids = ["f62", "f267", "f164", "f174"]
day1_names = ["Today_Ranking", "3-Day_Ranking", "5-Day_Ranking", "10-Day_Ranking"]  #  ["今日排行", "3日排行", "5日排行", "10日排行"]

day2_ids = ["f62", "f164", "f174"]
day2_names = ["Today_Ranking", "5-Day_Ranking", "10-Day_Ranking"]  # ["今日排行", "5日排行", "10日排行"]

# 请求的基础参数，用于API调用时的配置
BASE_PARAMS = {
    "cb": None,  # 流量 ID（动态更新）
    "fid": None,  # 日类型（动态更新）
    "po": "1",
    "pz": "50",  # 每页显示条数
    "pn": None,  # 页码（动态更新）
    "np": "1",
    "fltt": "2",
    "invt": "2",
    "ut": "b2884a393a59ad64002292a3e90d46a5",
    "fs": None,  # 名称（动态更新）
    "fields": None
}

# 选择的字段ID，用于不同类型的流数据查询
fields_ids = ["f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
              "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
              "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
              "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13"]


def process_diff_today(diff, cnt, flow_id, day):
    from collections import OrderedDict
    return OrderedDict([
        ("Index", cnt),
        ("Code", diff["f12"]),
        ("Name", diff["f14"]),
        ("Latest_Price", diff["f2"] if flow_id == 1 else "N/A"),
        (day + "_Change_Percentage", diff["f3"]),  # "涨跌幅"
        (day + "_Main_Flow", {  # "主力净流入"
            "Net_Amount": diff["f62"],
            "Net_Percentage": diff["f184"],
        }),
        (day + "_Extra_Large_Order_Flow", {  # "超大单净流入"
            "Net_Amount": diff["f66"],
            "Net_Percentage": diff["f69"],
        }),
        (day + "_Large_Order_Flow", {  # "大单净流入"
            "Net_Amount": diff["f72"],
            "Net_Percentage": diff["f75"],
        }),
        (day + "_Medium_Order_Flow", {  # "中单净流入"
            "Net_Amount": diff["f78"],
            "Net_Percentage": diff["f81"],
        }),
        (day + "_Small_Order_Flow", {  # "小单净流入"
            "Net_Amount": diff["f84"],
            "Net_Percentage": diff["f87"],
        }),
    ])


def process_diff_3_day(diff, cnt, flow_id, day):
    from collections import OrderedDict
    return OrderedDict([
        ("Index", cnt),
        ("Code", diff["f12"]),
        ("Name", diff["f14"]),
        ("Latest_Price", diff["f2"] if flow_id == 1 else "N/A"),
        (day + "_Change_Percentage", diff["f127"]),
        (day + "_Main_Flow", {
            "Net_Amount": diff["f267"],
            "Net_Percentage": diff["f268"],
        }),
        (day + "_Extra_Large_Order_Flow", {
            "Net_Amount": diff["f269"],
            "Net_Percentage": diff["f270"],
        }),
        (day + "_Large_Order_Flow", {
            "Net_Amount": diff["f271"],
            "Net_Percentage": diff["f272"],
        }),
        (day + "_Medium_Order_Flow", {
            "Net_Amount": diff["f273"],
            "Net_Percentage": diff["f274"],
        }),
        (day + "_Small_Order_Flow", {
            "Net_Amount": diff["f275"],
            "Net_Percentage": diff["f276"],
        }),
    ])


def process_diff_5_day(diff, cnt, flow_id, day):
    from collections import OrderedDict
    return OrderedDict([
        ("Index", cnt),
        ("Code", diff["f12"]),
        ("Name", diff["f14"]),
        ("Latest_Price", diff["f2"] if flow_id == 1 else "N/A"),
        (day + "_Change_Percentage", diff["f109"]),
        (day + "_Main_Flow", {
            "Net_Amount": diff["f164"],
            "Net_Percentage": diff["f165"],
        }),
        (day + "_Extra_Large_Order_Flow", {
            "Net_Amount": diff["f166"],
            "Net_Percentage": diff["f167"],
        }),
        (day + "_Large_Order_Flow", {
            "Net_Amount": diff["f168"],
            "Net_Percentage": diff["f169"],
        }),
        (day + "_Medium_Order_Flow", {
            "Net_Amount": diff["f170"],
            "Net_Percentage": diff["f171"],
        }),
        (day + "_Small_Order_Flow", {
            "Net_Amount": diff["f172"],
            "Net_Percentage": diff["f173"],
        }),
    ])


def process_diff_10_day(diff, cnt, flow_id, day):
    from collections import OrderedDict
    return OrderedDict([
        ("Index", cnt),
        ("Code", diff["f12"]),
        ("Name", diff["f14"]),
        ("Latest_Price", diff["f2"] if flow_id == 1 else "N/A"),
        (day + "_Change_Percentage", diff["f160"]),
        (day + "_Main_Flow", {
            "Net_Amount": diff["f174"],
            "Net_Percentage": diff["f175"],
        }),
        (day + "_Extra_Large_Order_Flow", {
            "Net_Amount": diff["f176"],
            "Net_Percentage": diff["f177"],
        }),
        (day + "_Large_Order_Flow", {
            "Net_Amount": diff["f178"],
            "Net_Percentage": diff["f179"],
        }),
        (day + "_Medium_Order_Flow", {
            "Net_Amount": diff["f180"],
            "Net_Percentage": diff["f181"],
        }),
        (day + "_Small_Order_Flow", {
            "Net_Amount": diff["f182"],
            "Net_Percentage": diff["f183"],
        }),
    ])


process_diff = [process_diff_today, process_diff_3_day, process_diff_5_day, process_diff_10_day]

