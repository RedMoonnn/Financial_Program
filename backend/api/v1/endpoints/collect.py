"""
数据采集路由模块
"""

from crawler.crawler import run_collect, run_collect_all
from fastapi import APIRouter, BackgroundTasks, Body, Depends

from api.middleware import APIResponse
from api.v1.endpoints.auth import get_admin_user
from api.v1.endpoints.collect_validators import validate_collect_params

router = APIRouter(prefix="/collect", tags=["collect"])


@router.post("/collect_v2")
async def collect_v2(
    flow_choice: int = Body(..., description="1:Stock_Flow, 2:Sector_Flow"),
    market_choice: int = Body(None, description="市场选项，仅flow_choice=1时有效"),
    detail_choice: int = Body(None, description="板块选项，仅flow_choice=2时有效"),
    day_choice: int = Body(..., description="日期选项"),
    pages: int = Body(1, description="采集页数"),
    admin_user=Depends(get_admin_user),  # 需要管理员权限
):
    """
    单组合数据采集

    采集数据并返回：
    - table: 表名
    - count: 采集条数
    - crawl_time: 采集时间
    - data: 采集到的全部数据（用于前端Echarts实时渲染）

    - **flow_choice**: 资金流类型选择（1:Stock_Flow, 2:Sector_Flow）
    - **market_choice**: 市场选项（仅flow_choice=1时有效，1~8）
    - **detail_choice**: 板块选项（仅flow_choice=2时有效，1~3）
    - **day_choice**: 日期选项
    - **pages**: 采集页数（默认1）
    """
    # 统一使用验证函数进行参数校验
    validate_collect_params(flow_choice, market_choice, detail_choice, day_choice)

    result = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
    return APIResponse.success(data=result, message="采集成功")


@router.post("/collect_all_v2")
async def collect_all_v2(
    background_tasks: BackgroundTasks,
    admin_user=Depends(get_admin_user),  # 需要管理员权限
):
    """
    全量数据采集

    启动后台任务进行全量数据采集
    """
    background_tasks.add_task(run_collect_all)
    return APIResponse.success(message="全量采集任务已启动")
