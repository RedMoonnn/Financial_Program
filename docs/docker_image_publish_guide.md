# Docker 镜像发布指南

## 1. 需要发布哪些镜像？

对于前后端分离的金融数据平台，通常需要发布以下镜像：
- **前端镜像**（如 financial_program_frontend）：包含 React/Antd 前端代码及依赖。
- **后端镜像**（如 financial_program_backend）：包含 FastAPI 后端代码及依赖。
- **（可选）数据库、Redis、MinIO 等第三方服务**：一般直接用官方镜像，无需自定义发布。

## 2. 镜像构建流程

### 方法一：单独构建（docker build）
1. **本地构建镜像**（以 frontend 为例）：
   ```bash
   docker build -t your_dockerhub_username/financial_program_frontend:latest ./frontend
   docker build -t your_dockerhub_username/financial_program_backend:latest ./backend
   ```
   > 推荐加上版本号，如 :v1.0.0，便于后续升级和回滚。

2. **本地测试镜像**
   ```bash
   docker run -it -p 5173:5173 your_dockerhub_username/financial_program_frontend:latest
   docker run -it -p 8000:8000 your_dockerhub_username/financial_program_backend:latest
   ```

### 方法二：一键多服务构建（docker compose build）
- 你也可以直接在项目根目录下用 compose 一键构建所有服务镜像：
  ```bash
  docker compose build
  # 或只构建 frontend 服务
  docker compose build frontend
  # 或只构建 backend 服务
  docker compose build backend
  ```
- 这样会自动读取 docker-compose.yml 里的 build 配置，按服务名构建镜像。
- 构建完成后可用 `docker compose up -d` 启动服务。

#### docker build 与 docker compose build 的区别
- `docker build` 适合单独构建某个目录下的镜像，需手动指定上下文和 tag。
- `docker compose build` 适合多服务项目，一键批量构建，自动按 yml 配置命名和管理镜像。
- 推荐团队开发、CI/CD、微服务场景优先用 compose build。

## 3. 推送镜像到 Docker Hub

1. **登录 Docker Hub**
   ```bash
   docker login
   # 输入你的 Docker Hub 用户名和密码
   ```
2. **推送镜像**
   ```bash
   docker push your_dockerhub_username/financial_program_frontend:latest
   docker push your_dockerhub_username/financial_program_backend:latest
   ```

## 4. 推送到私有仓库（如 Harbor、阿里云等）
- 替换镜像名为私有仓库地址，如：
  ```bash
  docker build -t registry.example.com/your_project/financial_program_frontend:v1.0.0 ./frontend
  docker push registry.example.com/your_project/financial_program_frontend:v1.0.0
  ```
- 首次推送需登录私有仓库：
  ```bash
  docker login registry.example.com
  ```

## 5. 版本管理建议
- 每次发布建议打上明确的 tag（如 v1.0.0、v1.1.0 等），不要只用 latest。
- 生产环境部署时，指定具体 tag，避免因 latest 变动导致不可预期的问题。

## 6. 常见注意事项
- **不要将敏感信息（如 .env、密钥）打包进镜像**。
- .dockerignore 文件要配置好，避免 node_modules、.git 等无关内容进入镜像。
- 构建前端镜像时，建议用多阶段构建，只保留最终产物，减小镜像体积。
- 推送前可用 `docker images` 检查本地镜像。

## 7. 参考命令速查
```bash
# 用 compose 一键构建所有服务
cd 项目根目录
docker compose build
# 只构建 frontend 服务
docker compose build frontend
# 只构建 backend 服务
docker compose build backend

# 登录并推送
docker login
# 推送前端
docker push your_dockerhub_username/financial_program_frontend:v1.0.0
# 推送后端
docker push your_dockerhub_username/financial_program_backend:v1.0.0
```

## 8. 参考链接
- [Docker Hub 官网](https://hub.docker.com/)
- [Docker 官方文档](https://docs.docker.com/engine/reference/commandline/push/)
- [多阶段构建官方文档](https://docs.docker.com/build/building/multi-stage/) 