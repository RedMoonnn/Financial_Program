"""
应用启动脚本
直接运行此文件可以启动应用（开发环境）
生产环境建议使用 uvicorn 命令直接运行 app.main:app
"""

import uvicorn

if __name__ == "__main__":
    # 注意：数据库初始化会在 app.main 的 lifespan 中自动执行
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
