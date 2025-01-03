# 保持热爱 奔赴山海

url = "https://push2.eastmoney.com/api/qt/clist/get"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

flows_id = ["jquery112309245886249999282_1733396772298",
            "jQuery112309570655592067874_1733410054611"]

flows_names = ["个股资金流", "板块资金流"]

Market_ids = ["m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
              "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
              "m:1+t:2+f:!2,m:1+t:23+f:!2",
              "m:1+t:23+f:!2",
              "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
              "m:0+t:80+f:!2",
              "m:1+t:3+f:!2",
              "m:0+t:7+f:!2"]

Market_names = ["全部股票",
                "沪深A股",
                "沪市A股",
                "科创板",
                "深市A股",
                "创业板",
                "沪市B股",
                "深市B股"]

Detail_flows_ids = ["m:90+t:2", "m:90+t:3", "m:90+t:1"]
Detail_flows_names = ["行业资金流", "概念资金流", "地域资金流"]

Day1_ids = ["f62", "f267", "f164", "f174"]
Day1_names = ["今日排行", "3日排行", "5日排行", "10日排行"]

Day2_ids = ["f62",  "f164", "f174"]
Day2_names = ["今日排行", "5日排行", "10日排行"]

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

fields_ids=["f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
            "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
            "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
            "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13"]


def process_diff_today(diff, cnt, flow_id, Day):
    """处理单个 diff 数据并返回有序字典"""
    from collections import OrderedDict
    return OrderedDict([
        ("序号", cnt),
        ("代码", diff["f12"]),
        ("名称", diff["f14"]),
        ("最新价", diff["f2"] if flow_id == 1 else "N/A"),
        (Day + "涨跌幅", diff["f3"]),
        (Day + "主力净流入", {
            "净额": diff["f62"],
            "净占比": diff["f184"],
        }),
        (Day + "超大单净流入", {
            "净额": diff["f66"],
            "净占比": diff["f69"],
        }),
        (Day + "大单净流入", {
            "净额": diff["f72"],
            "净占比": diff["f75"],
        }),
        (Day + "中单净流入", {
            "净额": diff["f78"],
            "净占比": diff["f81"],
        }),
        (Day + "小单净流入", {
            "净额": diff["f84"],
            "净占比": diff["f87"],
        }),
    ])


def process_diff_3_day(diff, cnt, flow_id, Day):
    """处理单个 diff 数据并返回有序字典"""
    from collections import OrderedDict
    return OrderedDict([
        ("序号", cnt),
        ("代码", diff["f12"]),
        ("名称", diff["f14"]),
        ("最新价", diff["f2"] if flow_id == 1 else "N/A"),
        (Day + "涨跌幅", diff["f127"]),
        (Day + "主力净流入", {
            "净额": diff["f267"],
            "净占比": diff["f268"],
        }),
        (Day + "超大单净流入", {
            "净额": diff["f269"],
            "净占比": diff["f270"],
        }),
        (Day + "大单净流入", {
            "净额": diff["f271"],
            "净占比": diff["f272"],
        }),
        (Day + "中单净流入", {
            "净额": diff["f273"],
            "净占比": diff["f274"],
        }),
        (Day + "小单净流入", {
            "净额": diff["f275"],
            "净占比": diff["f276"],
        }),
    ])


def process_diff_5_day(diff, cnt, flow_id, Day):
    """处理单个 diff 数据并返回有序字典"""
    from collections import OrderedDict
    return OrderedDict([
        ("序号", cnt),
        ("代码", diff["f12"]),
        ("名称", diff["f14"]),
        ("最新价", diff["f2"] if flow_id == 1 else "N/A"),
        (Day + "涨跌幅", diff["f109"]),
        (Day + "主力净流入", {
            "净额": diff["f164"],
            "净占比": diff["f165"],
        }),
        (Day + "超大单净流入", {
            "净额": diff["f166"],
            "净占比": diff["f167"],
        }),
        (Day + "大单净流入", {
            "净额": diff["f168"],
            "净占比": diff["f169"],
        }),
        (Day + "中单净流入", {
            "净额": diff["f170"],
            "净占比": diff["f171"],
        }),
        (Day + "小单净流入", {
            "净额": diff["f172"],
            "净占比": diff["f173"],
        }),
    ])


def process_diff_10_day(diff, cnt, flow_id, Day):
    """处理单个 diff 数据并返回有序字典"""
    from collections import OrderedDict
    return OrderedDict([
        ("序号", cnt),
        ("代码", diff["f12"]),
        ("名称", diff["f14"]),
        ("最新价", diff["f2"] if flow_id == 1 else "N/A"),
        (Day + "涨跌幅", diff["f160"]),
        (Day + "主力净流入", {
            "净额": diff["f174"],
            "净占比": diff["f175"],
        }),
        (Day + "超大单净流入", {
            "净额": diff["f176"],
            "净占比": diff["f177"],
        }),
        (Day + "大单净流入", {
            "净额": diff["f178"],
            "净占比": diff["f179"],
        }),
        (Day + "中单净流入", {
            "净额": diff["f180"],
            "净占比": diff["f181"],
        }),
        (Day + "小单净流入", {
            "净额": diff["f182"],
            "净占比": diff["f183"],
        }),
    ])


process_diff = [process_diff_today, process_diff_3_day, process_diff_5_day, process_diff_10_day]
