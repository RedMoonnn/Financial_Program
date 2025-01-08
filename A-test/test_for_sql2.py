# 保持热爱 奔赴山海
import mysql.connector
import os

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

# 图片文件路径
image_path = \
    ("D:/Desktop/Py_Practice/Web_Crawler/Specific_Case/EastMoney_Crawler/data/Stock_Flow-All_Stocks-Today/Stock_Flow-All_Stocks-Today.png")

# 读取图片文件为二进制数据
image_data = open(image_path, 'rb').read()

# 创建一个测试表（如果尚未存在）
table_name = "Images_data"
title = "test"
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS `{table_name}` (
    `Index` INT AUTO_INCREMENT PRIMARY KEY,
    `Title` VARCHAR(100),
    `Image_data` LONGBLOB NOT NULL
);
""")

# 插入图片数据
cursor.execute(f"""
INSERT INTO `{table_name}` (Title,`Image_data`) 
VALUES (%(Title)s,%(Image_data)s)
ON DUPLICATE KEY UPDATE `Title` = VALUES(`Title`),`Image_data` = VALUES(`Image_data`)
""", {"Title":title,"Image_data":image_data })

# 提交更改
conn.commit()
print(f"Image has been successfully stored in the table `{table_name}`.")

# 关闭游标和数据库连接
cursor.close()
conn.close()
