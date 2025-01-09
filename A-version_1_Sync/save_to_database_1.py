# 保持热爱 奔赴山海
import os

import mysql.connector


def store_data_to_db(data, title, day_name):
    """
    将数据存储到数据库
    :param data: 爬取的结果数据列表
    :param title: 表名
    :param day_name: 字段的动态前缀
    """

    # 先定义一个功能函数
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    # MySQL 连接配置
    db_config = {
        'host': ' 127.0.0.1',  # 数据库地址
        'user': 'root',  # 用户名
        'password': '',  # 密码
        'database': 'financial_web_crawler',  # 使用的数据库
    }

    # 连接到 MySQL 数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 替换表名中的特殊字符
    table1_name = title.replace("-", "_").replace("·", "_").replace(" ", "_")
    prefix = day_name.replace(" ", "_")  # 动态字段前缀

    # 创建表
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table1_name}` (
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

    for record in data:
        # 插入或更新数据的 SQL 语句
        cursor.execute(f"""
            INSERT INTO `{table1_name}` (
                `Index`, `Code`, `Name`, `Latest_Price`, `{prefix}_Change_Percentage`,
                `{prefix}_Main_Flow_Net_Amount`, `{prefix}_Main_Flow_Net_Percentage`,
                `{prefix}_Extra_Large_Order_Flow_Net_Amount`, `{prefix}_Extra_Large_Order_Flow_Net_Percentage`,
                `{prefix}_Large_Order_Flow_Net_Amount`, `{prefix}_Large_Order_Flow_Net_Percentage`,
                `{prefix}_Medium_Order_Flow_Net_Amount`, `{prefix}_Medium_Order_Flow_Net_Percentage`,
                `{prefix}_Small_Order_Flow_Net_Amount`, `{prefix}_Small_Order_Flow_Net_Percentage`
            ) VALUES (
                %(Index)s, %(Code)s, %(Name)s, %(Latest_Price)s, %(Change_Percentage)s,
                %(Main_Flow_Net_Amount)s, %(Main_Flow_Net_Percentage)s,
                %(Extra_Large_Order_Flow_Net_Amount)s, %(Extra_Large_Order_Flow_Net_Percentage)s,
                %(Large_Order_Flow_Net_Amount)s, %(Large_Order_Flow_Net_Percentage)s,
                %(Medium_Order_Flow_Net_Amount)s, %(Medium_Order_Flow_Net_Percentage)s,
                %(Small_Order_Flow_Net_Amount)s, %(Small_Order_Flow_Net_Percentage)s
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
            "Latest_Price": float(record["Latest_Price"]) if is_float(record["Latest_Price"]) else None,
            "Change_Percentage": float(record.get(f"{prefix}_Change_Percentage", 0)) if is_float(
                record.get(f"{prefix}_Change_Percentage", '')) else None,
            "Main_Flow_Net_Amount": float(record.get(f"{prefix}_Main_Flow", {}).get("Net_Amount", None)) if is_float(
                record.get(f"{prefix}_Main_Flow", {}).get("Net_Amount", '')) else None,
            "Main_Flow_Net_Percentage": float(
                record.get(f"{prefix}_Main_Flow", {}).get("Net_Percentage", None)) if is_float(
                record.get(f"{prefix}_Main_Flow", {}).get("Net_Percentage", '')) else None,
            "Extra_Large_Order_Flow_Net_Amount": float(
                record.get(f"{prefix}_Extra_Large_Order_Flow", {}).get("Net_Amount", None)) if is_float(
                record.get(f"{prefix}_Extra_Large_Order_Flow", {}).get("Net_Amount", '')) else None,
            "Extra_Large_Order_Flow_Net_Percentage": float(
                record.get(f"{prefix}_Extra_Large_Order_Flow", {}).get("Net_Percentage", None)) if is_float(
                record.get(f"{prefix}_Extra_Large_Order_Flow", {}).get("Net_Percentage", '')) else None,
            "Large_Order_Flow_Net_Amount": float(
                record.get(f"{prefix}_Large_Order_Flow", {}).get("Net_Amount", None)) if is_float(
                record.get(f"{prefix}_Large_Order_Flow", {}).get("Net_Amount", '')) else None,
            "Large_Order_Flow_Net_Percentage": float(
                record.get(f"{prefix}_Large_Order_Flow", {}).get("Net_Percentage", None)) if is_float(
                record.get(f"{prefix}_Large_Order_Flow", {}).get("Net_Percentage", '')) else None,
            "Medium_Order_Flow_Net_Amount": float(
                record.get(f"{prefix}_Medium_Order_Flow", {}).get("Net_Amount", None)) if is_float(
                record.get(f"{prefix}_Medium_Order_Flow", {}).get("Net_Amount", '')) else None,
            "Medium_Order_Flow_Net_Percentage": float(
                record.get(f"{prefix}_Medium_Order_Flow", {}).get("Net_Percentage", None)) if is_float(
                record.get(f"{prefix}_Medium_Order_Flow", {}).get("Net_Percentage", '')) else None,
            "Small_Order_Flow_Net_Amount": float(
                record.get(f"{prefix}_Small_Order_Flow", {}).get("Net_Amount", None)) if is_float(
                record.get(f"{prefix}_Small_Order_Flow", {}).get("Net_Amount", '')) else None,
            "Small_Order_Flow_Net_Percentage": float(
                record.get(f"{prefix}_Small_Order_Flow", {}).get("Net_Percentage", None)) if is_float(
                record.get(f"{prefix}_Small_Order_Flow", {}).get("Net_Percentage", '')) else None
        })

    # 图片文件路径
    image_path = f"../data/{title}/{title}.png"

    # 确保图片文件存在
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return  # 或者抛出异常

    # 读取图片文件为二进制数据
    try:
        image_data = open(image_path, 'rb').read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return  # 或者抛出异常

    # 创建一个存储图片信息的表
    table2_name = "Images_data"
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS `{table2_name}` (
        `Index` INT AUTO_INCREMENT PRIMARY KEY,
        `Title` VARCHAR(100) UNIQUE,
        `Image_data` LONGBLOB NOT NULL
    );
    """)



    # 插入图片数据
    cursor.execute(f"""
        INSERT INTO `{table2_name}` (Title, `Image_data`) 
        VALUES (%(Title)s, %(Image_data)s)
        ON DUPLICATE KEY UPDATE 
            `Image_data` = VALUES(`Image_data`)
    """, {
        "Title": title, "Image_data": image_data
    })

    conn.commit()

    print(f"Table `{table1_name}` has been successfully updated.")
    print(f"Table `{table2_name}` has been successfully updated.")

    # 关闭游标
    cursor.close()

    # 关闭数据库连接
    conn.close()
