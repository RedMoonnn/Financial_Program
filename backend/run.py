import uvicorn
from services.services import init_db, DATA_READY

init_db()

# 新增：启动爬虫定时任务
from threading import Thread
from services.services import TaskService, FlowDataService
from crawler.crawler import fetch_flow_data
import time

def start_crawler_job():
    from apscheduler.schedulers.background import BackgroundScheduler
    import services.services as services_mod
    def crawl_and_save():
        # 遍历所有可用分类，采集全量数据
        all_market_types = ['A股', '港股', '板块', '行业', '概念', '地域']
        all_flow_types = ['资金流向']
        all_periods = ['today', '3d', '5d', '10d']
        for market_type in all_market_types:
            for flow_type in all_flow_types:
                for period in all_periods:
                    task = TaskService.create_task(flow_type, market_type, period, pages=1)
                    data_list = fetch_flow_data(flow_type, market_type, period, pages=1)
                    FlowDataService.save_flow_data(data_list, task.id)
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {market_type}-{flow_type}-{period} 数据采集完成，共{len(data_list)}条")
        # 采集完成后设置全局状态
        services_mod.DATA_READY = True
        print("全量数据采集完成，DATA_READY已置为True")
    # 启动时先全量采集一次
    crawl_and_save()
    # 定时增量刷新
    def refresh_job():
        services_mod.DATA_READY = False
        crawl_and_save()
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_job, 'interval', minutes=5)
    scheduler.start()
    print("爬虫定时任务已启动，每5分钟自动刷新数据")

# 启动定时任务线程，避免阻塞主进程
Thread(target=start_crawler_job, daemon=True).start()

if __name__ == '__main__':
    uvicorn.run('api.api:app', host='0.0.0.0', port=8000, reload=True) 