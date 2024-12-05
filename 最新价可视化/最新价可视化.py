import json
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties

# 设置中文字体
font_path = "C:/Windows/Fonts/simhei.ttf"  # 根据操作系统修改字体路径
font_prop = FontProperties(fname=font_path)  # 使用指定的字体
rcParams['font.family'] = font_prop.get_name()  # 全局设置字体

# 读取数据
json_file_path = '../实时资金流排行.json'
with open(json_file_path, 'r', encoding='utf-8') as f:
    json_loaded = json.load(f)

data = json_loaded["data"]

names = [item["名称"] for item in data]
prices = [item["最新价"] for item in data]

# 可视化
plt.figure(figsize=(24, 6))  # 设置更合适的图表大小
plt.bar(names, prices, color='skyblue', width=0.6)

# 添加标题和标签
plt.title('股票最新价格柱状图', fontsize=24, fontweight='black', color=(1, 0.5, 0.5))
plt.xlabel('股票名称', fontsize=14)
plt.ylabel('最新价', fontsize=14)

# 添加数值标注
for i, price in enumerate(prices):
    plt.text(i, price + 0.5, f'{price:.2f}', ha='center', fontsize=12)

# 显示图表
plt.xticks(rotation=45, ha='right')  # 旋转x轴标签，防止重叠
plt.tight_layout()  # 自动调整布局，避免内容被裁剪

# 保存图表
plt.savefig('最新价可视化.png')

print("end")
