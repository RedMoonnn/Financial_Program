import aiomysql

# 异步存储数据到数据库
async def store_data_to_db(data, title, day_name, db_config):
    """
    将数据存储到数据库
    :param data: 爬取的结果数据列表
    :param title: 表名
    :param day_name: 字段的动态前缀
    :param db_config: 数据库配置
    """
    # 替换表名中的特殊字符
    table_name = title.replace("-", "_").replace("·", "_").replace(" ", "_")
    prefix = day_name.replace(" ", "_")  # 动态字段前缀

    # 创建表和插入数据的操作在异步函数中执行
    await execute_db_operations(db_config, table_name, prefix, data)


# 执行数据库操作，创建表并插入数据
async def execute_db_operations(db_config, table_name, prefix, data):
    """
    执行数据库操作，创建表并插入数据
    :param db_config: 数据库配置
    :param table_name: 表名
    :param prefix: 字段的动态前缀
    :param data: 爬取的数据
    """
    async with aiomysql.connect(**db_config) as conn:
        async with conn.cursor() as cursor:

            def is_float(value):
                try:
                    float(value)
                    return True
                except ValueError:
                    return False

            # 创建表
            await cursor.execute(f"""
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

            # 插入或更新数据
            for record in data:
                await cursor.execute(f"""
                    INSERT INTO `{table_name}` (
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
                    ) AS new_values ON DUPLICATE KEY UPDATE
                        `Code` = new_values.`Code`,
                        `Name` = new_values.`Name`,
                        `Latest_Price` = new_values.`Latest_Price`,
                        `{prefix}_Change_Percentage` = new_values.`{prefix}_Change_Percentage`,
                        `{prefix}_Main_Flow_Net_Amount` = new_values.`{prefix}_Main_Flow_Net_Amount`,
                        `{prefix}_Main_Flow_Net_Percentage` = new_values.`{prefix}_Main_Flow_Net_Percentage`,
                        `{prefix}_Extra_Large_Order_Flow_Net_Amount` = new_values.`{prefix}_Extra_Large_Order_Flow_Net_Amount`,
                        `{prefix}_Extra_Large_Order_Flow_Net_Percentage` = new_values.`{prefix}_Extra_Large_Order_Flow_Net_Percentage`,
                        `{prefix}_Large_Order_Flow_Net_Amount` = new_values.`{prefix}_Large_Order_Flow_Net_Amount`,
                        `{prefix}_Large_Order_Flow_Net_Percentage` = new_values.`{prefix}_Large_Order_Flow_Net_Percentage`,
                        `{prefix}_Medium_Order_Flow_Net_Amount` = new_values.`{prefix}_Medium_Order_Flow_Net_Amount`,
                        `{prefix}_Medium_Order_Flow_Net_Percentage` = new_values.`{prefix}_Medium_Order_Flow_Net_Percentage`,
                        `{prefix}_Small_Order_Flow_Net_Amount` = new_values.`{prefix}_Small_Order_Flow_Net_Amount`,
                        `{prefix}_Small_Order_Flow_Net_Percentage` = new_values.`{prefix}_Small_Order_Flow_Net_Percentage`
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
            await conn.commit()
            print(f"Table `{table_name}` has been successfully updated.")
