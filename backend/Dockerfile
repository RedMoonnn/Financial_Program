FROM python:3.12-slim

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（充分利用缓存）
COPY pyproject.toml .
# 注：如果 build context 是 backend 目录，需要确保 backend 内有自己的 pyproject.toml
# 如果希望锁定版本，建议将根目录的 uv.lock 也纳入考虑，但为了简单起见，我们先基于 backend 自己的配置

# 安装依赖 (不安装开发依赖，且不创建虚拟环境直接装在系统里以减小镜像体积)
RUN uv pip install --system --no-cache .

# 复制源码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "run.py"]
