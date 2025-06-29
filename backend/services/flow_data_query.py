import pymysql
from datetime import datetime, timedelta
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))

def get_all_latest_flow_data():
    """
    遍历所有Stock_Flow_%和Sector_Flow_%分表，合并所有数据，返回结构化列表。
    """
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'financial_web_crawler'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    # 查找所有分表
    cursor.execute("SHOW TABLES LIKE 'Stock_Flow_%'")
    stock_tables = [row[0] for row in cursor.fetchall()]
    cursor.execute("SHOW TABLES LIKE 'Sector_Flow_%'")
    sector_tables = [row[0] for row in cursor.fetchall()]
    all_tables = stock_tables + sector_tables
    results = []
    for table in all_tables:
        try:
            cursor.execute(f"SELECT code, name, flow_type, market_type, period, latest_price, change_percentage, main_flow_net_amount, main_flow_net_percentage, extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, large_order_flow_net_amount, large_order_flow_net_percentage, medium_order_flow_net_amount, medium_order_flow_net_percentage, small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time FROM `{table}` ORDER BY crawl_time DESC")
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    'type': 'stock' if row[2] == 'Stock_Flow' else 'sector',
                    'flow_type': row[2],
                    'market_type': row[3],
                    'period': row[4],
                    'data': {
                        'code': row[0],
                        'name': row[1],
                        'latest_price': row[5],
                        'change_percentage': row[6],
                        'main_flow_net_amount': row[7],
                        'main_flow_net_percentage': row[8],
                        'extra_large_order_flow_net_amount': row[9],
                        'extra_large_order_flow_net_percentage': row[10],
                        'large_order_flow_net_amount': row[11],
                        'large_order_flow_net_percentage': row[12],
                        'medium_order_flow_net_amount': row[13],
                        'medium_order_flow_net_percentage': row[14],
                        'small_order_flow_net_amount': row[15],
                        'small_order_flow_net_percentage': row[16],
                        'crawl_time': str(row[17])
                    }
                })
        except Exception as e:
            print(f"查询表{table}出错: {e}")
    cursor.close()
    conn.close()
    return results

def query_table_data(table_name, limit=50):
    """
    查询指定表名的最新N条数据，返回结构化列表。
    """
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'financial_web_crawler'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    results = []
    try:
        cursor.execute(f"SHOW TABLES LIKE %s", (table_name,))
        if not cursor.fetchone():
            return []
        cursor.execute(f"SELECT code, name, flow_type, market_type, period, latest_price, change_percentage, main_flow_net_amount, main_flow_net_percentage, extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, large_order_flow_net_amount, large_order_flow_net_percentage, medium_order_flow_net_amount, medium_order_flow_net_percentage, small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time FROM `{table_name}` ORDER BY crawl_time DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        for row in rows:
            results.append({
                'type': 'stock' if row[2] == 'Stock_Flow' else 'sector',
                'flow_type': row[2],
                'market_type': row[3],
                'period': row[4],
                'data': {
                    'code': row[0],
                    'name': row[1],
                    'latest_price': row[5],
                    'change_percentage': row[6],
                    'main_flow_net_amount': row[7],
                    'main_flow_net_percentage': row[8],
                    'extra_large_order_flow_net_amount': row[9],
                    'extra_large_order_flow_net_percentage': row[10],
                    'large_order_flow_net_amount': row[11],
                    'large_order_flow_net_percentage': row[12],
                    'medium_order_flow_net_amount': row[13],
                    'medium_order_flow_net_percentage': row[14],
                    'small_order_flow_net_amount': row[15],
                    'small_order_flow_net_percentage': row[16],
                    'crawl_time': str(row[17])
                }
            })
    except Exception as e:
        print(f"查询表{table_name}出错: {e}")
    cursor.close()
    conn.close()
    return results

def query_stock_flow_data(stock_name, limit=100):
    """
    遍历所有Stock_Flow_%和Sector_Flow_%分表，查找包含该股票名的最新N条数据。
    """
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'financial_web_crawler'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    # 查找所有分表
    cursor.execute("SHOW TABLES LIKE 'Stock_Flow_%'")
    stock_tables = [row[0] for row in cursor.fetchall()]
    cursor.execute("SHOW TABLES LIKE 'Sector_Flow_%'")
    sector_tables = [row[0] for row in cursor.fetchall()]
    all_tables = stock_tables + sector_tables
    results = []
    for table in all_tables:
        try:
            cursor.execute(f"SELECT code, name, flow_type, market_type, period, latest_price, change_percentage, main_flow_net_amount, main_flow_net_percentage, extra_large_order_flow_net_amount, extra_large_order_flow_net_percentage, large_order_flow_net_amount, large_order_flow_net_percentage, medium_order_flow_net_amount, medium_order_flow_net_percentage, small_order_flow_net_amount, small_order_flow_net_percentage, crawl_time FROM `{table}` WHERE name LIKE %s ORDER BY crawl_time DESC LIMIT %s", (f"%{stock_name}%", limit))
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    'type': 'stock' if row[2] == 'Stock_Flow' else 'sector',
                    'flow_type': row[2],
                    'market_type': row[3],
                    'period': row[4],
                    'data': {
                        'code': row[0],
                        'name': row[1],
                        'latest_price': row[5],
                        'change_percentage': row[6],
                        'main_flow_net_amount': row[7],
                        'main_flow_net_percentage': row[8],
                        'extra_large_order_flow_net_amount': row[9],
                        'extra_large_order_flow_net_percentage': row[10],
                        'large_order_flow_net_amount': row[11],
                        'large_order_flow_net_percentage': row[12],
                        'medium_order_flow_net_amount': row[13],
                        'medium_order_flow_net_percentage': row[14],
                        'small_order_flow_net_amount': row[15],
                        'small_order_flow_net_percentage': row[16],
                        'crawl_time': str(row[17])
                    }
                })
        except Exception as e:
            print(f"查询表{table}出错: {e}")
    cursor.close()
    conn.close()
    # 按时间降序，最多limit条
    results = sorted(results, key=lambda x: x['data']['crawl_time'], reverse=True)
    return results[:limit]

if __name__ == '__main__':

    table_name = input("请输入要分析的表名（如Sector_Flow_Concept_Flow_10_Day）：").strip()
    if table_name:
        table_data = query_table_data(table_name, limit=50)
        print(f"表{table_name}最新50条数据：{table_data[:2]} ... 共{len(table_data)}条")
        if table_data:
            try:
                from ai.deepseek import DeepseekAgent
                # 只传递核心字段，防止token溢出
                slim_data = [
                    {
                        'type': d['type'],
                        'flow_type': d['flow_type'],
                        'market_type': d['market_type'],
                        'period': d['period'],
                        'data': {
                            'code': d['data']['code'],
                            'name': d['data']['name'],
                            'main_flow_net_amount': d['data']['main_flow_net_amount'],
                            'main_flow_net_percentage': d['data']['main_flow_net_percentage'],
                            'change_percentage': d['data']['change_percentage'],
                            'crawl_time': d['data']['crawl_time']
                        }
                    } for d in table_data
                ]
                user_message = f"请帮我分析一下表 {table_name} 的资金流情况"
                result = DeepseekAgent.analyze(slim_data, user_message=user_message, style="专业")
                print("\n=== Deepseek分析结果 ===\n")
                print(result)
            except Exception as e:
                print(f"调用Deepseek分析出错: {e}")
        else:
            print(f"表{table_name}无数据！") 