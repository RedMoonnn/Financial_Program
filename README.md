# EastMoney Crawler

## 项目简介
本项目旨在通过爬取东方财富网数据，实现数据存储和可视化展示。项目的主要功能包括：
- 爬取指定数据并存储到 MySQL 数据库
- 使用动态字段命名构建数据库表
- 生成数据可视化图片

## 项目结构
├── A-test  
├── A-version_0_chinese  
├── data/  
│   ├── titleA  
│   │   ├── 可视化图片.png  
│   │   ├── 可视化图片.png  
│   ├── titleB  
│   │   ├── 可视化图片.png  
│   │   ├── 可视化图片.png  
│   ├── ...  
│   │   ├── ...  
│   │   ├── ...  
├── main/  
│   ├── main_1.py  
│   ├── source_data_1.py  
│   ├── visualize_1.py  
├── README.md  
└── requirements.txt  




## 文件说明
### 1. `A-test`
测试文件，开发过程中使用的临时代码或逻辑验证文件，无需查看。

### 2. `A-version_0_chinese`
该文件为项目的第0版，包含中文注释，但存在无法构建数据库的问题，不推荐使用。

### 3. `data/`
#### - 'title'
数据集的名称
##### - `爬取数据.json`
包含从东方财富网爬取的原始数据，格式为 JSON。
##### - `可视化图片.png`
基于爬取数据生成的可视化图片，用于展示数据分析结果。

### 4. `main/`
该文件夹包含项目的主要代码：
- `main_1.py`：项目的主函数文件，负责调用数据爬取、存储、以及可视化功能。
- `source_data_1.py`：包含数据处理逻辑，供主函数调用。
- `visualize_1.py`：用于生成可视化图片，依据爬取的数据生成图表。

### 5. `requirements.txt`
列出了项目所需的 Python 包。使用以下命令安装所需库：
```bash
pip install -r requirements.txt
