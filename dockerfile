FROM python:3.11

WORKDIR /app

COPY backend/ backend/
COPY frontend/ frontend/
COPY requirements.txt .

# 安装 Node.js 和 npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# 安装后端依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装前端依赖
WORKDIR /app/frontend
RUN npm install

# 回到主目录
WORKDIR /app

# 启动脚本：同时启动后端和前端
CMD bash -c "python3 -m backend.app & cd frontend && npm start"