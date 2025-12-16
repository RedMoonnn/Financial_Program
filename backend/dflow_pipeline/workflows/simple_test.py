"""
简化版测试工作流 - 用于学习 dflow 基本概念

这个工作流不使用 Slices，只执行单个任务，便于理解 dflow 的核心概念。
"""

from dflow import Workflow, Step
from dflow.python import OP, OPIO, OPIOSign, Artifact, PythonOPTemplate
from pathlib import Path
import json


# ============================================================
# 第一步：定义 OP (Operation)
# ============================================================
# OP 是 dflow 的最小执行单元，类似于函数
# 每个 OP 必须定义：
#   1. 输入签名 (get_input_sign) - 声明接收什么参数
#   2. 输出签名 (get_output_sign) - 声明返回什么结果
#   3. 执行逻辑 (execute) - 实际的业务代码


class SimpleHelloOP(OP):
    """
    最简单的 OP 示例 - 只打印一条消息

    这个 OP 演示了：
    - 如何定义输入输出签名
    - 如何在 execute 中处理输入并返回输出
    """

    @classmethod
    def get_input_sign(cls):
        """
        定义输入签名

        OPIOSign 是一个字典，key 是参数名，value 是类型
        支持的基本类型：str, int, float, bool, list, dict
        支持的特殊类型：Artifact(Path) - 用于传递文件
        """
        return OPIOSign(
            {
                "name": str,  # 输入一个名字
                "count": int,  # 输入一个数字
            }
        )

    @classmethod
    def get_output_sign(cls):
        """
        定义输出签名

        输出也是一个字典，定义这个 OP 会产出什么
        """
        return OPIOSign(
            {
                "message": str,  # 输出一条消息
                "result": int,  # 输出计算结果
            }
        )

    @OP.exec_sign_check  # 装饰器：自动检查输入输出类型
    def execute(self, op_in: OPIO) -> OPIO:
        """
        执行逻辑 - 这是 OP 的核心

        Args:
            op_in: OPIO 字典，包含所有输入参数

        Returns:
            OPIO 字典，包含所有输出结果
        """
        # 1. 从 op_in 获取输入参数
        name = op_in["name"]
        count = op_in["count"]

        # 2. 执行业务逻辑
        message = f"Hello, {name}! Your count is {count}."
        result = count * 2

        print(f"[SimpleHelloOP] 执行完成: {message}")

        # 3. 返回 OPIO，key 必须匹配 output_sign
        return OPIO(
            {
                "message": message,
                "result": result,
            }
        )


class CrawlSingleStockOP(OP):
    """
    简化版爬虫 OP - 只采集一个市场的今日数据

    这个 OP 演示了：
    - 如何使用 Artifact 传递文件
    - 如何进行网络请求
    - 实际的数据采集逻辑
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "market_name": str,  # 市场名称，如 "All_Stocks"
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "data_file": Artifact(Path),  # 输出文件 (Artifact 类型)
                "count": int,  # 采集数量
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        import requests

        market_name = op_in["market_name"]

        # 东方财富 API
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # 全部 A 股的过滤参数
        params = {
            "fid": "f62",
            "pn": "1",
            "pz": 10,  # 只采集前 10 条，便于测试
            "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f124,f1,f13",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }

        print(f"[CrawlSingleStockOP] 开始采集 {market_name} 数据...")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            data = response.json()

            diff_list = data.get("data", {}).get("diff", [])

            # 处理数据
            results = []
            for diff in diff_list:
                item = {
                    "code": diff.get("f12", ""),
                    "name": diff.get("f14", ""),
                    "latest_price": diff.get("f2", 0),
                    "change_percentage": diff.get("f3", 0),
                    "main_flow_net_amount": diff.get("f62", 0),
                }
                results.append(item)

            print(f"[CrawlSingleStockOP] 采集到 {len(results)} 条数据")

        except Exception as e:
            print(f"[CrawlSingleStockOP] 采集失败: {e}")
            results = []

        # 保存到文件 (Artifact 必须是文件)
        output_path = Path("/tmp/crawl_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {"market": market_name, "data": results},
                f,
                ensure_ascii=False,
                indent=2,
            )

        return OPIO(
            {
                "data_file": output_path,  # 返回文件路径，dflow 会自动上传到 S3
                "count": len(results),
            }
        )


# ============================================================
# 第二步：创建 Workflow
# ============================================================


def create_hello_workflow(name: str = "hello-dflow") -> Workflow:
    """
    创建最简单的 Hello World 工作流

    这个工作流演示了：
    - 如何创建 Workflow
    - 如何创建 PythonOPTemplate
    - 如何创建 Step 并添加到 Workflow
    """
    # 1. 创建 Workflow 实例
    wf = Workflow(name=name)

    # 2. 创建 Template
    # PythonOPTemplate 将 OP 包装成可以在 K8s 中运行的容器
    hello_template = PythonOPTemplate(
        SimpleHelloOP,  # 要执行的 OP 类
        image="python:3.9-slim",  # Docker 镜像
    )

    # 3. 创建 Step
    # Step 是 Workflow 的执行单元，关联 Template 和参数
    hello_step = Step(
        name="say-hello",  # Step 名称
        template=hello_template,  # 使用的 Template
        parameters={  # 传递给 OP 的参数
            "name": "dflow学习者",
            "count": 42,
        },
    )

    # 4. 将 Step 添加到 Workflow
    wf.add(hello_step)

    return wf


def create_crawl_workflow(name: str = "simple-crawl") -> Workflow:
    """
    创建简化版爬虫工作流

    这个工作流演示了：
    - 如何使用 Artifact (文件传递)
    - 如何处理依赖包
    """
    wf = Workflow(name=name)

    # 获取 dflow_pipeline 目录（用于上传到容器）
    from pathlib import Path

    backend_dir = Path(__file__).parent.parent.parent.absolute()
    dflow_pipeline_dir = backend_dir / "dflow_pipeline"

    # 创建爬虫 Template
    crawl_template = PythonOPTemplate(
        CrawlSingleStockOP,
        image="python:3.9-slim",
        python_packages=[dflow_pipeline_dir],  # 上传代码到容器
        # pre_script 在执行前运行，用于安装依赖
        pre_script="import subprocess; subprocess.run(['pip', 'install', 'requests', '-q'])\n",
    )

    # 创建 Step
    crawl_step = Step(
        name="crawl-stock",
        template=crawl_template,
        parameters={
            "market_name": "All_Stocks",
        },
    )

    wf.add(crawl_step)

    return wf


# ============================================================
# 运行入口
# ============================================================


if __name__ == "__main__":
    import sys

    # 导入配置
    from .. import config as _  # noqa: F401

    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        # Debug 模式：本地运行，不需要 K8s
        from dflow import config as dflow_config

        dflow_config["mode"] = "debug"
        print("Running in DEBUG mode (local execution)")
        wf = create_hello_workflow()
    else:
        # 正常模式：提交到 Argo
        wf = create_crawl_workflow()

    print(f"Submitting workflow: {wf.name}")
    wf.submit()
    print(f"Workflow submitted! ID: {wf.id}")
