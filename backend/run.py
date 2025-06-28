import uvicorn
from services.services import init_db, DATA_READY

init_db()

# 新增：启动爬虫定时任务
from threading import Thread
from services.services import TaskService, FlowDataService, set_data_ready
from crawler.crawler import run_collect, market_names, detail_flows_names
import time

def start_crawler_job():
    from apscheduler.schedulers.background import BackgroundScheduler
    import services.services as services_mod
    def crawl_and_save():
        set_data_ready(False)
        # 个股资金流 Stock_Flow
        for market_choice in range(1, 9):
            for day_choice in range(1, 5):
                flow_choice = 1
                detail_choice = None
                pages = 1
                res = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
                print(f"Stock_Flow | 市场: {market_names[market_choice-1]} | 周期: {['today','3d','5d','10d'][day_choice-1]} | 采集条数: {res['count']}")
        # 板块资金流 Sector_Flow
        for detail_choice in range(1, 4):
            for day_choice in range(1, 4):
                flow_choice = 2
                market_choice = None
                pages = 1
                res = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
                print(f"Sector_Flow | 板块: {detail_flows_names[detail_choice-1]} | 周期: {['today','5d','10d'][day_choice-1]} | 采集条数: {res['count']}")
        set_data_ready(True)
        print("全量数据采集完成，DATA_READY已置为True")
    # 启动时先全量采集一次
    crawl_and_save()
    # 定时增量刷新
    def refresh_job():
        set_data_ready(False)
        crawl_and_save()
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_job, 'interval', minutes=5)
    scheduler.start()
    print("爬虫定时任务已启动，每5分钟自动刷新数据")

# 启动定时任务线程，避免阻塞主进程
Thread(target=start_crawler_job, daemon=True).start()

if __name__ == '__main__':
    # uvicorn.run('api.api:app', host='0.0.0.0', port=8000, reload=True) 
    uvicorn.run('api.api:app', host='0.0.0.0', port=8000) 