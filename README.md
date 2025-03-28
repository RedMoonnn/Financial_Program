# 东方财富数据采集系统

## 项目概述

本项目是一个基于Python的数据采集系统，专注于从东方财富网获取股票市场数据。系统支持数据采集、存储、分析和可视化，为投资决策提供数据支持。

### 核心功能

- 🔄 **实时数据采集**：从东方财富网实时获取股票市场数据
- 📊 **数据可视化**：自动生成数据分析图表
- 💾 **多样化存储**：支持MySQL数据库存储和MinIO对象存储
- 🔧 **自动化部署**：支持自动化数据采集和处理流程

## 系统架构

### 项目结构
```
.
├── program/              # 核心代码目录
│   ├── main_1.py        # 主程序入口
│   ├── auto_exe_1.py    # 自动化执行脚本
│   ├── source_data_1.py # 数据处理逻辑
│   ├── save_to_database_1.py  # MySQL数据库操作
│   ├── save_to_minio.py      # MinIO存储操作
│   ├── visualize_1.py        # 数据可视化
│   ├── read_images.py        # 图片处理工具
│   ├── auto_exe_linux.png    # Linux系统执行时间统计
│   └── auto_exe_windows.png  # Windows系统执行时间统计
├── data/                # 数据存储目录(已添加到.gitignore)
│   ├── *.json          # 原始数据
│   └── *.png           # 可视化图表
├── .env                # 环境配置文件
├── requirements.txt    # 项目依赖
└── README.md          # 项目文档
```

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+
- MinIO Server

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置说明
1. 复制`.env.example`为`.env`
2. 配置数据库连接信息：
   ```
   MYSQL_PASSWORD=your_password
   ```
3. 配置MinIO存储信息：
   ```
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=your_access_key
   MINIO_SECRET_KEY=your_secret_key
   MINIO_BUCKET_NAME=data
   MINIO_SECURE=False
   ```

### 运行程序
```bash
# 进入程序目录
cd program

# 运行主程序（单次采集）
python main_1.py

# 执行自动化采集（批量采集）
python auto_exe_1.py
```

## 功能说明

### 数据采集
- **市场数据**：支持A股、港股等多个市场的数据采集
- **资金流向**：主力资金、行业资金流向等
- **排名数据**：涨跌幅、成交量等多维度排名
- **时间周期**：支持日、周、月等多个时间维度

### 数据存储
- **JSON文件**：原始数据本地存储，包含完整的采集信息
- **MySQL数据库**：结构化存储，支持复杂查询
- **MinIO对象存储**：图表文件云存储，支持远程访问

### 数据可视化
- **资金流向图**：展示主力资金流入流出情况
- **市场趋势图**：展示市场整体走势
- **性能统计图**：展示程序执行效率（Linux/Windows对比）

## 开发说明

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解
- 完整的注释文档

### 性能优化
- 优化数据库操作
- 批量数据处理
- 执行时间统计

## 维护说明

### 注意事项
- 定期检查数据库存储空间
- 及时更新依赖包版本
- 确保MinIO服务正常运行

## 许可证
MIT License
