# 保持热爱 奔赴山海

import matplotlib
import mysql.connector
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# 切换后端为支持图形的选项
matplotlib.use('TkAgg')

# MySQL 连接配置
db_config = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 用户名
    'password': "",  # 密码（需要设置环境变量）
    'database': 'financial_web_crawler',  # 使用的数据库
}

# 连接到 MySQL 数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 选择要读取的表
title = "Stock_Flow-All_Stocks-Today"

# 从数据库读取图片数据
cursor.execute(f"SELECT Image_data FROM `Images_data` WHERE `Title` = %s", (title,))
image_data = cursor.fetchone()[0]  # 获取二进制数据,cursor.fetchone()从执行的查询中获取一行结果

# 将二进制数据转换为图像
image = Image.open(BytesIO(image_data))

# 使用 matplotlib 显示图像
plt.imshow(image)
plt.axis('off')
plt.show()

# 关闭游标和数据库连接
cursor.close()
conn.close()
