import mysql.connector
from datetime import datetime


def database_operations(db_config, table_name, data):
    """
    执行数据库操作，包括创建表、清空表、插入数据和查询数据。
    """
    # 连接到 MySQL 数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 创建表
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        created_at DATETIME
    );
    """
    cursor.execute(create_table_query)

    # 清空表数据
    truncate_query = f"TRUNCATE TABLE {table_name}"
    cursor.execute(truncate_query)

    # 插入数据
    insert_query = f"""
    INSERT INTO {table_name} (name, email, created_at)
    VALUES (%s, %s, %s)
    """
    cursor.executemany(insert_query, data)
    conn.commit()

    # 查询数据
    select_query = f"SELECT * FROM {table_name}"
    cursor.execute(select_query)
    results = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    conn.close()

    return results


def main():
    # MySQL 连接配置
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'financial_web_crawler',
    }

    # 动态表名和插入的数据
    table_name = "test_table"
    new_data = [
        ("Alice Smith", "alice.smith@example.com", datetime.now()),
        ("Bob Johnson", "bob.johnson@example.com", datetime.now()),
        ("Charlie Brown", "charlie.brown@example.com", datetime.now()),
    ]

    # 调用功能函数执行数据库操作
    results = database_operations(db_config, table_name, new_data)

    # 输出查询结果
    if results:
        print("数据插入成功:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Created At: {row[3]}")
    else:
        print("表中没有数据")


if __name__ == "__main__":
    main()
