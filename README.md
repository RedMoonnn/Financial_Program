# EastMoney Crawler

## 项目简介
本项目旨在通过爬取东方财富网数据，实现数据存储和可视化展示。项目的主要功能包括：
- 爬取指定数据并存储到 MySQL 数据库
- 使用动态字段命名构建数据库表
- 生成数据可视化图片

## 项目结构
├── main/ # 主文件夹  
│   ├── main_1.py # 主函数入口  
│   ├── source_data_1.py # 数据处理所需文件  
│   ├── visualize_1.py # 数据可视化生成函数  
├── data/ # 爬取数据目录  
│   ├── 爬取数据.json # 爬取的数据文件  
│   ├── 可视化图片.png # 数据可视化生成的图片  
├── README.md # 项目说明文件  
└── requirements.txt # Python依赖库文件

## 文件说明
### 1. `main/`
该文件夹包含项目的主要代码：
- `main_1.py`：项目的主函数文件，负责调用数据爬取、存储、以及可视化功能。
- `source_data_1.py`：包含数据处理逻辑，供主函数调用。
- `visualize_1.py`：用于生成可视化图片，依据爬取的数据生成图表。

### 2. `data/`
#### - `爬取数据.json`
包含从东方财富网爬取的原始数据，格式为 JSON。
#### - `可视化图片.png`
基于爬取数据生成的可视化图片，用于展示数据分析结果。

### 3. `requirements.txt`
列出了项目所需的 Python 包。使用以下命令安装所需库：
```bash
pip install -r requirements.txt
