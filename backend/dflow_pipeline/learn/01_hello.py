#!/usr/bin/env python3
"""
dflow 学习教程 - 第1课：Hello World

这是最简单的 dflow 示例，帮助你理解核心概念。

运行方式：
    cd /home/chy/dev/Financial_Program/backend
    PYTHONPATH=. python dflow_pipeline/learn/01_hello.py
"""

# ============================================================
# 第一部分：导入必要的模块
# ============================================================

from dflow import Workflow, Step  # Workflow 和 Step
from dflow.python import OP, OPIO, OPIOSign  # OP 相关
from dflow.python import PythonOPTemplate  # 模板


# ============================================================
# 第二部分：定义一个 OP（操作）
# ============================================================
#
# OP 就像一个函数，但有严格的输入输出定义
#
# 普通函数：
#   def greet(name):
#       return f"Hello, {name}!"
#
# dflow OP：
#   class GreetOP(OP):
#       输入: name (str)
#       输出: message (str)
#       执行: 返回 "Hello, {name}!"


class GreetOP(OP):
    """
    最简单的 OP：接收一个名字，返回问候语
    """

    @classmethod
    def get_input_sign(cls):
        """
        定义输入签名 - 这个 OP 需要什么输入？

        返回一个字典：
        - key: 参数名
        - value: 参数类型（str, int, float, bool, list, dict）
        """
        return OPIOSign(
            {
                "name": str,  # 需要一个字符串类型的 name 参数
            }
        )

    @classmethod
    def get_output_sign(cls):
        """
        定义输出签名 - 这个 OP 会输出什么？
        """
        return OPIOSign(
            {
                "message": str,  # 输出一个字符串类型的 message
            }
        )

    @OP.exec_sign_check  # 这个装饰器会自动检查输入输出类型是否正确
    def execute(self, op_in: OPIO) -> OPIO:
        """
        执行逻辑 - 这是实际的业务代码

        参数:
            op_in: 一个字典，包含所有输入参数

        返回:
            OPIO: 一个字典，包含所有输出结果
        """
        # 1. 从 op_in 中获取输入
        name = op_in["name"]

        # 2. 执行业务逻辑（这里就是简单的字符串拼接）
        message = f"Hello, {name}! 欢迎学习 dflow!"

        # 3. 打印一下（会出现在 Pod 日志中）
        print(f"[GreetOP] 生成消息: {message}")

        # 4. 返回结果（必须是 OPIO 字典，key 要匹配 output_sign）
        return OPIO(
            {
                "message": message,
            }
        )


# ============================================================
# 第三部分：创建工作流
# ============================================================


def create_workflow():
    """
    创建一个包含 GreetOP 的工作流
    """

    # 步骤 1：创建 Workflow
    # Workflow 是整个工作流的容器
    wf = Workflow(name="hello-dflow-tutorial")

    # 步骤 2：创建 Template
    # Template 告诉 dflow 如何在 K8s 中运行这个 OP
    # - 用什么 Docker 镜像
    # - 需要安装什么依赖
    template = PythonOPTemplate(
        GreetOP,  # 要运行的 OP 类
        image="python:3.9-slim",  # 使用的 Docker 镜像
    )

    # 步骤 3：创建 Step
    # Step 是 Workflow 中的一个步骤，它连接了：
    # - Template（怎么运行）
    # - Parameters（传什么参数）
    step = Step(
        name="greet-step",  # 步骤名称
        template=template,  # 使用的模板
        parameters={  # 传递的参数（对应 OP 的 input_sign）
            "name": "小明",
        },
    )

    # 步骤 4：把 Step 添加到 Workflow
    wf.add(step)

    return wf


# ============================================================
# 第四部分：运行
# ============================================================

if __name__ == "__main__":
    # 设置 debug 模式（本地运行，不需要 K8s）
    from dflow import config

    config["mode"] = "debug"

    print("=" * 60)
    print("dflow 学习教程 - 第1课：Hello World")
    print("=" * 60)
    print()

    # 创建工作流
    print("1. 创建工作流...")
    wf = create_workflow()
    print(f"   工作流名称: {wf.name}")
    print()

    # 提交工作流
    print("2. 提交工作流（debug 模式会在本地执行）...")
    print("-" * 40)
    wf.submit()
    print("-" * 40)
    print()

    print("3. 完成！")
    print(f"   工作流 ID: {wf.id}")
    print()
    print("=" * 60)
    print("恭喜！你已经成功运行了第一个 dflow 工作流！")
    print("=" * 60)
