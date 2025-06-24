# Docker Compose 使用命令大全与容器化开发流程指南

## 一、常用命令大全

### 1. 构建镜像
```
docker compose build
```

### 2. 启动所有服务（前后台）
```
docker compose up
```

### 3. 启动并在后台运行
```
docker compose up -d
```

### 4. 关闭并移除所有容器
```
docker compose down
```

### 5. 关闭并移除容器、网络、卷
```
docker compose down -v --remove-orphans
```

### 6. 查看服务日志
```
docker compose logs -f
```

### 7. 查看容器状态
```
docker compose ps
```

### 8. 进入某个容器
```
docker compose exec <服务名> /bin/bash
```
如：
```
docker compose exec backend /bin/bash
```

### 9. 只重启某个服务
```
docker compose restart frontend
```

### 10. 构建并启动指定服务
```
docker compose up --build backend
```

### 11. 清理无用镜像/卷/网络
```
docker image prune -a -f
```
```
docker system prune -af
```

---

## 二、容器化开发流程

### 1. 目录结构建议
```
project-root/
  backend/           # 后端代码
  frontend/          # 前端代码
  data/              # 数据持久化目录（MySQL/Redis/MinIO等）
  docker-compose.yml # Compose主配置
  docs/              # 文档
```

### 2. 开发流程

1. **准备好 `docker-compose.yml`、`Dockerfile`、依赖文件（如 requirements.txt、package.json）**
2. **构建镜像**
   ```
   docker compose build
   ```
3. **启动所有服务**
   ```
   docker compose up
   ```
   - 前端开发环境：http://localhost:5173
   - 后端API：http://localhost:8000
4. **代码热重载**
   - 挂载 volumes，代码变更自动同步到容器，支持热重载开发。
5. **进入容器调试**
   ```
   docker compose exec backend /bin/bash
   ```
6. **查看日志**
   ```
   docker compose logs -f
   ```
7. **关闭服务**
   ```
   docker compose down
   ```
8. **清理环境**
   ```
   docker compose down -v --remove-orphans
   docker system prune -af
   ```

### 3. 常见问题与建议
- **镜像拉取慢/失败**：配置国内镜像加速器（如阿里云、DaoCloud等）。
- **端口冲突**：确保本地未占用5173、8000、3307、9001、9002、6379等端口。
- **数据持久化**：务必挂载 data 目录，防止容器重启数据丢失。
- **多开发者协作**：建议每人一份.env，避免端口/密码冲突。
- **升级Compose**：推荐使用 `docker compose`（V2插件），更稳定。

---

## 三、参考资料
- [Docker官方文档](https://docs.docker.com/compose/)
- [Compose命令对比](https://docs.docker.com/compose/cli-command/)
- [阿里云镜像加速器](https://developer.aliyun.com/article/29941)

---

如有更多团队协作、CI/CD、生产部署等需求，可进一步补充！ 