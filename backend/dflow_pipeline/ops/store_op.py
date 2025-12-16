"""
数据存储 OP - 将采集的数据存储到 MySQL
"""

import os
import json
from pathlib import Path
from typing import List
from dflow.python import OP, OPIO, OPIOSign, Artifact
import pymysql


def get_db_config():
    """获取数据库配置"""
    return {
        "host": os.getenv("MYSQL_HOST", "mysql"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "financial_web_crawler"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "charset": "utf8mb4",
    }


class StoreToMySQLOP(OP):
    """批量存储数据到 MySQL"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "data_files": Artifact(List[Path]),  # 多个数据文件
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "success": bool,
                "total_count": int,
                "tables": List[str],
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        data_files = op_in["data_files"]
        total_count = 0
        tables = []

        db_config = get_db_config()
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        try:
            for data_file in data_files:
                with open(data_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)

                table_name = file_data["table_name"]
                data = file_data["data"]

                if not data:
                    continue

                # 创建表
                self._create_table(cursor, table_name)

                # 清空表
                cursor.execute(f"TRUNCATE TABLE `{table_name}`;")

                # 插入数据
                for record in data:
                    self._insert_record(cursor, table_name, record)

                total_count += len(data)
                tables.append(table_name)

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

        return OPIO(
            {
                "success": True,
                "total_count": total_count,
                "tables": tables,
            }
        )

    def _create_table(self, cursor, table_name):
        """创建数据表"""
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                `Index` INT PRIMARY KEY AUTO_INCREMENT,
                `code` VARCHAR(10),
                `name` VARCHAR(50),
                `flow_type` VARCHAR(32),
                `market_type` VARCHAR(32),
                `period` VARCHAR(16),
                `latest_price` FLOAT,
                `change_percentage` FLOAT,
                `main_flow_net_amount` FLOAT,
                `main_flow_net_percentage` FLOAT,
                `extra_large_order_flow_net_amount` FLOAT,
                `extra_large_order_flow_net_percentage` FLOAT,
                `large_order_flow_net_amount` FLOAT,
                `large_order_flow_net_percentage` FLOAT,
                `medium_order_flow_net_amount` FLOAT,
                `medium_order_flow_net_percentage` FLOAT,
                `small_order_flow_net_amount` FLOAT,
                `small_order_flow_net_percentage` FLOAT,
                `crawl_time` DATETIME
            ) DEFAULT CHARSET=utf8mb4;
        """)

    def _insert_record(self, cursor, table_name, record):
        """插入单条记录"""
        cursor.execute(
            f"""
            INSERT INTO `{table_name}` (
                `code`, `name`, `flow_type`, `market_type`, `period`, `latest_price`,
                `change_percentage`, `main_flow_net_amount`, `main_flow_net_percentage`,
                `extra_large_order_flow_net_amount`, `extra_large_order_flow_net_percentage`,
                `large_order_flow_net_amount`, `large_order_flow_net_percentage`,
                `medium_order_flow_net_amount`, `medium_order_flow_net_percentage`,
                `small_order_flow_net_amount`, `small_order_flow_net_percentage`,
                `crawl_time`
            ) VALUES (
                %(code)s, %(name)s, %(flow_type)s, %(market_type)s, %(period)s, %(latest_price)s,
                %(change_percentage)s, %(main_flow_net_amount)s, %(main_flow_net_percentage)s,
                %(extra_large_order_flow_net_amount)s, %(extra_large_order_flow_net_percentage)s,
                %(large_order_flow_net_amount)s, %(large_order_flow_net_percentage)s,
                %(medium_order_flow_net_amount)s, %(medium_order_flow_net_percentage)s,
                %(small_order_flow_net_amount)s, %(small_order_flow_net_percentage)s,
                %(crawl_time)s
            )
        """,
            record,
        )


class StoreSingleFileOP(OP):
    """存储单个数据文件到 MySQL (用于并行存储)"""

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "data_file": Artifact(Path),
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "success": bool,
                "count": int,
                "table_name": str,
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        data_file = op_in["data_file"]

        with open(data_file, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        table_name = file_data["table_name"]
        data = file_data["data"]

        if not data:
            return OPIO(
                {
                    "success": True,
                    "count": 0,
                    "table_name": table_name,
                }
            )

        db_config = get_db_config()
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        try:
            # 创建表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    `Index` INT PRIMARY KEY AUTO_INCREMENT,
                    `code` VARCHAR(10),
                    `name` VARCHAR(50),
                    `flow_type` VARCHAR(32),
                    `market_type` VARCHAR(32),
                    `period` VARCHAR(16),
                    `latest_price` FLOAT,
                    `change_percentage` FLOAT,
                    `main_flow_net_amount` FLOAT,
                    `main_flow_net_percentage` FLOAT,
                    `extra_large_order_flow_net_amount` FLOAT,
                    `extra_large_order_flow_net_percentage` FLOAT,
                    `large_order_flow_net_amount` FLOAT,
                    `large_order_flow_net_percentage` FLOAT,
                    `medium_order_flow_net_amount` FLOAT,
                    `medium_order_flow_net_percentage` FLOAT,
                    `small_order_flow_net_amount` FLOAT,
                    `small_order_flow_net_percentage` FLOAT,
                    `crawl_time` DATETIME
                ) DEFAULT CHARSET=utf8mb4;
            """)

            # 清空表
            cursor.execute(f"TRUNCATE TABLE `{table_name}`;")

            # 插入数据
            for record in data:
                cursor.execute(
                    f"""
                    INSERT INTO `{table_name}` (
                        `code`, `name`, `flow_type`, `market_type`, `period`, `latest_price`,
                        `change_percentage`, `main_flow_net_amount`, `main_flow_net_percentage`,
                        `extra_large_order_flow_net_amount`, `extra_large_order_flow_net_percentage`,
                        `large_order_flow_net_amount`, `large_order_flow_net_percentage`,
                        `medium_order_flow_net_amount`, `medium_order_flow_net_percentage`,
                        `small_order_flow_net_amount`, `small_order_flow_net_percentage`,
                        `crawl_time`
                    ) VALUES (
                        %(code)s, %(name)s, %(flow_type)s, %(market_type)s, %(period)s, %(latest_price)s,
                        %(change_percentage)s, %(main_flow_net_amount)s, %(main_flow_net_percentage)s,
                        %(extra_large_order_flow_net_amount)s, %(extra_large_order_flow_net_percentage)s,
                        %(large_order_flow_net_amount)s, %(large_order_flow_net_percentage)s,
                        %(medium_order_flow_net_amount)s, %(medium_order_flow_net_percentage)s,
                        %(small_order_flow_net_amount)s, %(small_order_flow_net_percentage)s,
                        %(crawl_time)s
                    )
                """,
                    record,
                )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

        return OPIO(
            {
                "success": True,
                "count": len(data),
                "table_name": table_name,
            }
        )
