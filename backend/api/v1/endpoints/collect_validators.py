"""
数据采集参数验证模块
统一管理采集参数的验证逻辑
"""

from fastapi import HTTPException, status


def validate_collect_params(
    flow_choice: int, market_choice: int | None, detail_choice: int | None, day_choice: int
) -> None:
    """
    验证采集参数

    Args:
        flow_choice: 资金流类型选择（1:Stock_Flow, 2:Sector_Flow）
        market_choice: 市场选项（仅flow_choice=1时有效，1~8）
        detail_choice: 板块选项（仅flow_choice=2时有效，1~3）
        day_choice: 日期选项

    Raises:
        HTTPException: 如果参数验证失败
    """
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
