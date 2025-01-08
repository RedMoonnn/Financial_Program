# 保持热爱 奔赴山海
import mysql.connector
import os
from PIL import Image
from io import BytesIO

# MySQL 连接配置
db_config = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 用户名
    'password': os.getenv('MYSQL_PASSWORD'),  # 密码（需要设置环境变量）
    'database': 'financial_web_crawler',  # 使用的数据库
}

# 连接到 MySQL 数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 选择要读取的表和图像ID
table_name = "test_images"
image_id = 1  # 根据你存储图片的ID来选择

# 从数据库读取图片数据
cursor.execute(f"SELECT `Image_data` FROM `{table_name}` WHERE `ID` = %s", (image_id,))
image_data = cursor.fetchone()[0]  # 获取二进制数据,cursor.fetchone()从执行的查询中获取一行结果

# 将二进制数据转换为图像
image = Image.open(BytesIO(image_data))

# 显示图像
image.show()

# 关闭游标和数据库连接
cursor.close()
conn.close()
