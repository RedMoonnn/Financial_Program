# 保持热爱 奔赴山海

import json
import pprint
import requests
from datetime import datetime
from source_data import *
from visualize import visualize_data
import os
import mysql.connector
import json

# MySQL 连接配置
db_config = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',       # 用户名
    'password': '',  # 密码
    'database': 'financial_web_crawler',  # 使用的数据库
}

# 连接到 MySQL 数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def input_details(a, s):
    cnt = 0
    for i in range(len(a)):
        cnt += 1
        print(str(cnt) + "." + a[i])
    choice = input(s)
    return choice


def web_crawler(flow_id, name, day, page, Day, process_diff_id):
    datas = []
    cnt = 0

    for i in range(int(page)):
        params = BASE_PARAMS.copy()
        params.update({
            "cb": flows_id[flow_id - 1],
            "fid": day,
            "pn": str(i + 1),  # 当前页码
            "fs": name,
            "fields": fields_ids[process_diff_id]
        })

        # pprint.pprint(params)

        resp = requests.get(url, headers=headers, params=params)
        data = resp.text
        # pprint.pprint(data)

        start_index = data.find('(') + 1
        end_index = data.rfind(')')
        json_str = data[start_index:end_index]

        parsed_data = json.loads(json_str)
        # pprint.pprint(parsed_data)

        # 处理数据
        diff_list = parsed_data['data']['diff']
        # print(json.dumps(diff_list, ensure_ascii=False, indent=4))

        for diff in diff_list:
            cnt += 1

            # 调用处理函数
            # print(json.dumps(diff, ensure_ascii=False, indent=4))
            # print(process_diff[process_diff_id].__name__)
            datas.append(process_diff[process_diff_id](diff, cnt, flow_id, Day))

    return datas


def get_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    time = current_time
    return time


def get_datas():
    flow = int(input_details(flows_names, "请输入要查询的板块名称:"))
    print()

    if flow == 1:

        id = int(input_details(Market_names, "请输入要查询的股票类型:"))
        print()
        market_id = Market_ids[int(id) - 1]

        day1_id = int(input_details(Day1_names, "请输入要查询的天数:"))
        print()
        day1 = Day1_ids[day1_id - 1]
        Day = Day1_names[day1_id - 1].split("排行")[0]
        # print(day1, Day)

        process_diff_id = day1_id - 1

        page = input("请输入要查询的页数(每页50条信息):")
        print()

        datas = web_crawler(flow, market_id, day1, page, Day, process_diff_id)

        title = flows_names[flow - 1] + "-" + Market_names[id - 1] + "-" + Day1_names[day1_id - 1]

    elif flow == 2:

        id = int(input_details(Detail_flows_names, "请输入具体要查询的板块:"))
        print()
        detail_flows_name = Detail_flows_ids[int(id) - 1]

        day2_id = int(input_details(Day2_names, "请输入要查询的天数:"))
        print()
        day2 = Day2_ids[day2_id - 1]
        Day = Day2_names[day2_id - 1].split("排行")[0]

        if day2_id == 1: process_diff_id = 0
        elif day2_id == 2: process_diff_id = 2
        elif day2_id == 3: process_diff_id = 3

        page = "1"

        datas = web_crawler(flow, detail_flows_name, day2, page, Day, process_diff_id)

        title = flows_names[flow - 1] + "-" + Detail_flows_names[id - 1] + "-" + Day2_names[day2_id - 1]

    return datas, title, page, Day


datas, title, page, Day = get_datas()
time = get_time()

data_to_write = {
    "time": time,
    "title": title,
    "data": datas
}

json_data = json.dumps(data_to_write, ensure_ascii=False, indent=4)

file_name = title + ".json"


os.makedirs('data/' + title, exist_ok=True)

with open('data/'+title+'/'+file_name, 'w', encoding='utf-8') as f:
    f.write(json_data)
print(file_name + "已成功生成")

visualize_data(title, Day, page)
print(title + '.png' + "已成功生成")

