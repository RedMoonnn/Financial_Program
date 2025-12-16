#!/usr/bin/env python3
"""
dflow 学习教程 - 第2课：Step 链式调用

学习如何让多个 Step 顺序执行，并传递数据。

运行方式：
    cd /home/chy/dev/Financial_Program/backend
    PYTHONPATH=. python dflow_pipeline/learn/02_chain.py
"""

from dflow import Workflow, Step
from dflow.python import OP, OPIO, OPIOSign, PythonOPTemplate


# ============================================================
# 定义两个 OP：一个生成数据，一个处理数据
# ============================================================


class GenerateOP(OP):
    """
    第一个 OP：生成一个数字
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "base": int,  # 基础数字
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "number": int,  # 输出的数字
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        base = op_in["base"]
        result = base * 10  # 简单的计算

        print(f"[GenerateOP] 输入: {base}, 输出: {result}")

        return OPIO({"number": result})


class ProcessOP(OP):
    """
    第二个 OP：处理数字
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "number": int,  # 接收上一步的输出
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "result": str,  # 最终结果
            }
        )

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        number = op_in["number"]
        result = f"处理完成！最终数字是: {number + 1}"

        print(f"[ProcessOP] 输入: {number}, 输出: {result}")

        return OPIO({"result": result})


# ============================================================
# 创建工作流：两个 Step 顺序执行
# ============================================================


def create_workflow():
    wf = Workflow(name="chain-tutorial")

    # 创建两个 Template
    gen_template = PythonOPTemplate(GenerateOP, image="python:3.9-slim")
    proc_template = PythonOPTemplate(ProcessOP, image="python:3.9-slim")

    # Step 1: 生成数据
    step1 = Step(
        name="generate",
        template=gen_template,
        parameters={"base": 5},
    )
    wf.add(step1)

    # Step 2: 处理数据（使用 Step 1 的输出）
    # 关键：通过 step1.outputs.parameters["number"] 获取上一步的输出
    step2 = Step(
        name="process",
        template=proc_template,
        parameters={
            "number": step1.outputs.parameters["number"],  # 引用上一步的输出！
        },
    )
    wf.add(step2)

    return wf


# ============================================================
# 图示说明
# ============================================================
"""
执行流程：

    ┌─────────────────┐
    │   GenerateOP    │
    │   输入: base=5  │
    │   输出: 50      │
    └────────┬────────┘
             │
             │ number=50 (数据传递)
             │
             ▼
    ┌─────────────────┐
    │   ProcessOP     │
    │   输入: 50      │
    │   输出: "处理完成！最终数字是: 51"
    └─────────────────┘

关键点：
- step1.outputs.parameters["number"] 引用了 Step 1 的输出
- dflow 会自动处理数据传递
- 在 K8s 模式下，这些数据会通过 Argo 的参数系统传递
"""


if __name__ == "__main__":
    from dflow import config

    config["mode"] = "debug"

    print("=" * 60)
    print("dflow 学习教程 - 第2课：Step 链式调用")
    print("=" * 60)
    print()
    print("流程: GenerateOP(5) → 50 → ProcessOP(50) → '最终数字是: 51'")
    print()

    wf = create_workflow()

    print("执行工作流...")
    print("-" * 40)
    wf.submit()
    print("-" * 40)
    print()
    print("完成！两个 Step 顺序执行，数据成功传递。")
