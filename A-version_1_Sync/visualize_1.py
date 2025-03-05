# 保持热爱 奔赴山海

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties


def visualize_data(title, day, page):
    # 设置中文字体
    font_path = "C:/Windows/Fonts/msyh.ttc"  # 根据操作系统修改字体路径
    font_prop = FontProperties(fname=font_path)
    rcParams['font.family'] = font_prop.get_name()

    # 读取数据
    json_file_path = './data/' + title + '/' + title + '.json'

    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_loaded = json.load(f)

    data = json_loaded.get("data", [])

    # 提取数据
    names = [item["Name"] for item in data]

    prices = [
        float(item[day + "_Main_Flow"]["Net_Amount"]) / 1000000
        if isinstance(item[day + "_Main_Flow"]["Net_Amount"], (int, float)) or
           (isinstance(item[day + "_Main_Flow"]["Net_Amount"], str) and
            item[day + "_Main_Flow"]["Net_Amount"].replace(".", "", 1).isdigit())
        else 0
        for item in data
    ]

    # 获取时间信息，若无则使用默认值
    time_str = json_loaded.get("time", "None")
    time_text = f"time: {time_str}"

    # 创建x轴的坐标位置，并增加柱子间距
    x_positions = np.arange(len(names)) * 2

    # 可视化
    plt.figure(figsize=(10 * int(page), 6), dpi=240)  # 设置图表大小与分辨率
    plt.bar(x_positions, prices, color='skyblue', width=0.8)  # 设置宽度并对齐

    # 添加标题和标签
    plt.title(f'{title}-Main_Flow_Net_Amount', fontsize=18, fontweight='bold', color=(0.1, 0.3, 0.7))
    plt.xlabel('Stock Name', fontsize=14)
    plt.ylabel('Net inflow amount (in millions)', fontsize=14)

    # 添加y轴虚线网格线
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 显示时间在左上角
    plt.text(0.01, 0.99, time_text, ha='left', va='top', fontsize=12, color='black', transform=plt.gca().transAxes)

    # 显示图表
    plt.xticks(x_positions, names, rotation=45, ha='right', fontsize=8)  # 设置x轴标签位置和角度
    plt.tight_layout()  # 自动调整布局，避免内容被裁剪

    # 保存图表
    output_path = f"{title}.png"
    plt.savefig('./data/' + title + '/' + output_path)

    print(f"{title}.png has been successfully generated.")
