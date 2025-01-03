# 保持热爱 奔赴山海

import json
import pprint
import requests
from datetime import datetime
from source_data_1 import *
from visualize_1 import visualize_data
import os
import mysql.connector

# MySQL 连接配置
db_config = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 用户名
    'password': '',  # 密码
    'database': 'financial_web_crawler',  # 使用的数据库
}

# 连接到 MySQL 数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


def input_details(options, prompt):
    """打印用户可选项"""
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    choice = input(prompt)
    return choice


def web_crawler(flow_id, market_filter, day_filter, pages, day_name, process_func_id):
    """爬虫主体函数"""
    results = []
    counter = 0

    for i in range(int(pages)):
        params = BASE_PARAMS.copy()
        params.update({
            "cb": flows_id[flow_id - 1],
            "fid": day_filter,
            "pn": str(i + 1),  # 当前页码
            "fs": market_filter,
            "fields": fields_ids[process_func_id]
        })

        response = requests.get(url, headers=headers, params=params)
        data = response.text

        # 清洗爬取数据，除去原数据标识头
        start_index = data.find('(') + 1
        end_index = data.rfind(')')
        json_str = data[start_index:end_index]

        parsed_data = json.loads(json_str)
        diff_list = parsed_data['data']['diff']

        for diff in diff_list:
            counter += 1
            results.append(process_diff[process_func_id](diff, counter, flow_id, day_name))

    return results


def get_current_time():
    """获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_data():
    flow_choice = int(input_details(flows_names, "Select the category to query:"))
    print()

    if flow_choice == 1:
        market_choice = int(input_details(market_names, "Select the stock type:"))
        print()
        market_filter = market_ids[market_choice - 1]

        day_choice = int(input_details(day1_names, "Select the ranking duration:"))
        print()
        day_filter = day1_ids[day_choice - 1]
        day_name = day1_names[day_choice - 1].split("_Ranking")[0]

        process_func_id = day_choice - 1
        pages = input("Enter the number of pages to query (50 records per page):")
        print()

        data_results = web_crawler(flow_choice, market_filter, day_filter, pages, day_name, process_func_id)

        title = f"{flows_names[flow_choice - 1]}-{market_names[market_choice - 1]}-{day_name}"

    elif flow_choice == 2:
        detail_choice = int(input_details(detail_flows_names, "Select the specific category to query:"))
        print()
        detail_filter = detail_flows_ids[detail_choice - 1]

        day_choice = int(input_details(day2_names, "Select the ranking duration:"))
        print()
        day_filter = day2_ids[day_choice - 1]
        day_name = day2_names[day_choice - 1].split("_Ranking")[0]

        process_func_id = [0, 2, 3][day_choice - 1]
        pages = "1"

        data_results = web_crawler(flow_choice, detail_filter, day_filter, pages, day_name, process_func_id)

        title = f"{flows_names[flow_choice - 1]}-{detail_flows_names[detail_choice - 1]}-{day_name}"

    return data_results, title, pages, day_name


def store_data_to_db(data, title, day_name):
    """
    将数据存储到数据库
    :param data: 爬取的结果数据列表
    :param title: 表名
    :param day_name: 字段的动态前缀
    """
    # 替换表名中的特殊字符
    table_name = title.replace("-", "_").replace("·", "_").replace(" ", "_")
    prefix = day_name.replace(" ", "_")  # 动态字段前缀

    # 创建表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        `Index` INT PRIMARY KEY,
        `Code` VARCHAR(10),
        `Name` VARCHAR(50),
        `Latest_Price` FLOAT,
        `{prefix}_Change_Percentage` FLOAT,
        `{prefix}_Main_Flow_Net_Amount` FLOAT,
        `{prefix}_Main_Flow_Net_Percentage` FLOAT,
        `{prefix}_Extra_Large_Order_Flow_Net_Amount` FLOAT,
        `{prefix}_Extra_Large_Order_Flow_Net_Percentage` FLOAT,
        `{prefix}_Large_Order_Flow_Net_Amount` FLOAT,
        `{prefix}_Large_Order_Flow_Net_Percentage` FLOAT,
        `{prefix}_Medium_Order_Flow_Net_Amount` FLOAT,
        `{prefix}_Medium_Order_Flow_Net_Percentage` FLOAT,
        `{prefix}_Small_Order_Flow_Net_Amount` FLOAT,
        `{prefix}_Small_Order_Flow_Net_Percentage` FLOAT
    );
    """)

    # 插入数据
    for record in data:
        cursor.execute(f"""
        INSERT INTO `{table_name}` (
            `Index`, `Code`, `Name`, `Latest_Price`, `{prefix}_Change_Percentage`,
            `{prefix}_Main_Flow_Net_Amount`, `{prefix}_Main_Flow_Net_Percentage`,
            `{prefix}_Extra_Large_Order_Flow_Net_Amount`, `{prefix}_Extra_Large_Order_Flow_Net_Percentage`,
            `{prefix}_Large_Order_Flow_Net_Amount`, `{prefix}_Large_Order_Flow_Net_Percentage`,
            `{prefix}_Medium_Order_Flow_Net_Amount`, `{prefix}_Medium_Order_Flow_Net_Percentage`,
            `{prefix}_Small_Order_Flow_Net_Amount`, `{prefix}_Small_Order_Flow_Net_Percentage`
        ) VALUES (
            %(Index)s, %(Code)s, %(Name)s, %(Latest_Price)s, %(Change_Percentage)s,
            %(Main_Flow.Net_Amount)s, %(Main_Flow.Net_Percentage)s,
            %(Extra_Large_Order_Flow.Net_Amount)s, %(Extra_Large_Order_Flow.Net_Percentage)s,
            %(Large_Order_Flow.Net_Amount)s, %(Large_Order_Flow.Net_Percentage)s,
            %(Medium_Order_Flow.Net_Amount)s, %(Medium_Order_Flow.Net_Percentage)s,
            %(Small_Order_Flow.Net_Amount)s, %(Small_Order_Flow.Net_Percentage)s
        ) ON DUPLICATE KEY UPDATE
            `Code` = VALUES(`Code`),
            `Name` = VALUES(`Name`),
            `Latest_Price` = VALUES(`Latest_Price`),
            `{prefix}_Change_Percentage` = VALUES(`{prefix}_Change_Percentage`),
            `{prefix}_Main_Flow_Net_Amount` = VALUES(`{prefix}_Main_Flow_Net_Amount`),
            `{prefix}_Main_Flow_Net_Percentage` = VALUES(`{prefix}_Main_Flow_Net_Percentage`),
            `{prefix}_Extra_Large_Order_Flow_Net_Amount` = VALUES(`{prefix}_Extra_Large_Order_Flow_Net_Amount`),
            `{prefix}_Extra_Large_Order_Flow_Net_Percentage` = VALUES(`{prefix}_Extra_Large_Order_Flow_Net_Percentage`),
            `{prefix}_Large_Order_Flow_Net_Amount` = VALUES(`{prefix}_Large_Order_Flow_Net_Amount`),
            `{prefix}_Large_Order_Flow_Net_Percentage` = VALUES(`{prefix}_Large_Order_Flow_Net_Percentage`),
            `{prefix}_Medium_Order_Flow_Net_Amount` = VALUES(`{prefix}_Medium_Order_Flow_Net_Amount`),
            `{prefix}_Medium_Order_Flow_Net_Percentage` = VALUES(`{prefix}_Medium_Order_Flow_Net_Percentage`),
            `{prefix}_Small_Order_Flow_Net_Amount` = VALUES(`{prefix}_Small_Order_Flow_Net_Amount`),
            `{prefix}_Small_Order_Flow_Net_Percentage` = VALUES(`{prefix}_Small_Order_Flow_Net_Percentage`)
        """, {
            "Index": record["Index"],
            "Code": record["Code"],
            "Name": record["Name"],
            "Latest_Price": record["Latest_Price"],
            "Change_Percentage": record[f"{prefix}_Change_Percentage"],
            "Main_Flow.Net_Amount": record[f"{prefix}_Main_Flow"]["Net_Amount"],
            "Main_Flow.Net_Percentage": record[f"{prefix}_Main_Flow"]["Net_Percentage"],
            "Extra_Large_Order_Flow.Net_Amount": record[f"{prefix}_Extra_Large_Order_Flow"]["Net_Amount"],
            "Extra_Large_Order_Flow.Net_Percentage": record[f"{prefix}_Extra_Large_Order_Flow"]["Net_Percentage"],
            "Large_Order_Flow.Net_Amount": record[f"{prefix}_Large_Order_Flow"]["Net_Amount"],
            "Large_Order_Flow.Net_Percentage": record[f"{prefix}_Large_Order_Flow"]["Net_Percentage"],
            "Medium_Order_Flow.Net_Amount": record[f"{prefix}_Medium_Order_Flow"]["Net_Amount"],
            "Medium_Order_Flow.Net_Percentage": record[f"{prefix}_Medium_Order_Flow"]["Net_Percentage"],
            "Small_Order_Flow.Net_Amount": record[f"{prefix}_Small_Order_Flow"]["Net_Amount"],
            "Small_Order_Flow.Net_Percentage": record[f"{prefix}_Small_Order_Flow"]["Net_Percentage"]
        })

    conn.commit()
    print(f"Table `{table_name}` has been successfully updated.")


# 主程序调用
data, title, pages, day_name = get_data()
current_time = get_current_time()

# 文件存储
output_data = {
    "time": current_time,
    "title": title,
    "data": data
}
file_name = f"{title}.json"
os.makedirs(f'data/{title}', exist_ok=True)

with open(f'data/{title}/{file_name}', 'w', encoding='utf-8') as file:
    json.dump(output_data, file, ensure_ascii=False, indent=4)

print(f"{file_name} has been successfully generated.")

# 调用绘图函数
visualize_data(title, day_name, pages)

# 调用存储函数
store_data_to_db(data, title, day_name)
