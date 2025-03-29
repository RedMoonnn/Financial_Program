FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 文件
COPY requirements.txt /app/requirements.txt

# 复制代码到容器中
COPY . /app

# 安装 Python 依赖
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 应用端口
EXPOSE 8000

# 启动 Flask 应用
CMD ["python", "program/api.py"]