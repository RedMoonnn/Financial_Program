import uvicorn
from services.services import init_db, DATA_READY

init_db()

# 启动定时任务线程，避免阻塞主进程
if __name__ == '__main__':
    # uvicorn.run('api.api:app', host='0.0.0.0', port=8000, reload=True) 
    uvicorn.run('api.api:app', host='0.0.0.0', port=8000) 