"""
数据采集路由模块
"""

from crawler.crawler import run_collect, run_collect_all
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status

from api.v1.endpoints.auth import get_admin_user

router = APIRouter(prefix="/api", tags=["collect"])


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
    # 参数校验
    if flow_choice == 1:
        if market_choice is None or not (1 <= market_choice <= 8):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=1时，market_choice必须为1~8",
            )
        if day_choice not in [1, 2, 3, 4]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="day_choice必须为1~4"
            )
    elif flow_choice == 2:
        if detail_choice is None or not (1 <= detail_choice <= 3):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=2时，detail_choice必须为1~3",
            )
        if day_choice not in [1, 2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="flow_choice=2时，day_choice必须为1~3",
            )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="flow_choice必须为1或2")

    result = run_collect(flow_choice, market_choice, detail_choice, day_choice, pages)
    return result


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
    return {"msg": "全量采集任务已启动"}
