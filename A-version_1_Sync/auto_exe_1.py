import subprocess
import time

# 定义选项
categories_1 = ["1"]  # Stock_Flow 选项编号
categories_2 = ["2"]  # Sector_Flow 选项编号

# 选择 1 的情况：股票类型有 8 种，排名时长有 4 种
stock_types_1 = ["1", "2", "3", "4", "5", "6", "7", "8"]  # 8 种股票类型
ranking_durations_1 = ["1", "2", "3", "4"]  # 4 种排名时长

# 选择 2 的情况：股票类型有 3 种，排名时长有 3 种
stock_types_2 = ["1", "2", "3"]  # 3 种股票类型
ranking_durations_2 = ["1", "2", "3"]  # 3 种排名时长

# 定义 Python 脚本路径
script_path = "/root/DongFangCaifu/A-version_1_Sync/main_1.py"
python_executable = "/root/DongFangCaifu/.venv/bin/python"

# 定义计数器，打印到输出窗口
counter = 0

# 记录程序开始的时间
start_time = time.time()

# 处理 Stock_Flow（category = 1）
for category in categories_1:
    for stock_type in stock_types_1:
        for ranking_duration in ranking_durations_1:
            # 打印当前输入的组合
            # 构建输入流，模拟用户在控制台的输入操作
            inputs = f"{category}\n{stock_type}\n{ranking_duration}\n1\n"  # 默认选择第1页
            try:
                process = subprocess.run(
                    [python_executable, script_path],
                    input=inputs,
                    text=True,
                    capture_output=True,
                    encoding="utf-8"
                )
                # 打印脚本的输出结果
                print(process.stdout)
                # 打印当前输入的组合
                print(f"Running combination: {category}{stock_type}{ranking_duration}1")
                # 如果有错误输出，打印错误信息
                if process.stderr:
                    print(f"Error message: {process.stderr}")
                else:
                    # 打印当前的计时和数据表个数
                    counter += 1
                    elapsed_time = time.time() - start_time
                    print(f"Current number of data tables: {counter}, Elapsed time: {elapsed_time:.2f} seconds\n")
            except Exception as e:
                # 捕获异常并打印错误信息
                print(f"运行脚本时出错: {e}")

# 处理 Sector_Flow（category = 2）
for category in categories_2:
    for stock_type in stock_types_2:
        for ranking_duration in ranking_durations_2:
            # 构建输入流，模拟用户在控制台的输入操作
            inputs = f"{category}\n{stock_type}\n{ranking_duration}\n"
            try:
                # 使用 subprocess 调用脚本并传递输入
                process = subprocess.run(
                    [python_executable, script_path],  # 指定 Python 可执行文件和脚本路径
                    input=inputs,                     # 将输入传递给脚本的标准输入
                    text=True,                        # 输入和输出为字符串格式
                    capture_output=True,              # 捕获脚本的标准输出和错误输出
                    encoding="utf-8"                  # 明确指定使用 UTF-8 编码来读取输出
                )
                # 打印脚本的输出结果
                print(process.stdout)
                # 打印当前输入的组合
                print(f"Running combination: {category}{stock_type}{ranking_duration}")
                # 如果有错误输出，打印错误信息
                if process.stderr:
                    print(f"错误信息: {process.stderr}")
                else:

                    # 打印当前的计时和数据表个数
                    counter += 1
                    elapsed_time = time.time() - start_time
                    print(f"Current number of data tables: {counter}, Elapsed time: {elapsed_time:.2f} seconds\n")
            except Exception as e:
                # 捕获异常并打印错误信息
                print(f"运行脚本时出错: {e}")

# 打印总的运行时间和平均时间
total_time = time.time() - start_time
print(f"\nTotal run time: {total_time:.2f} seconds")
print(f"Average run time: {total_time / 41:.2f} seconds")
# 打印成功输出率
print(f"Success rate: {(counter / 41) * 100:.2f}%")
