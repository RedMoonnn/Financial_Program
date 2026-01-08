import uvicorn
from services.init_db import init_db

init_db()

# 启动定时任务线程，避免阻塞主进程
if __name__ == "__main__":
    # 使用新的应用入口
    # uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
