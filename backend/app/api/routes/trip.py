"""旅行规划API路由"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ...agents.trip_planner_agent import get_trip_planner_agent
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
)
from ...services.trip_history_service import (
    TripHistoryService,
    get_trip_history_service,
)

router = APIRouter(prefix="/trip", tags=["旅行规划"])


def get_planner():
    """获取旅行规划器，允许测试替换。"""
    return get_trip_planner_agent()


def get_history_service() -> TripHistoryService:
    """获取历史记录服务，允许测试替换。"""
    return get_trip_history_service()


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
def plan_trip(
    request: TripRequest,
    agent=Depends(get_planner),
    history_service: TripHistoryService = Depends(get_history_service),
):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)
        history_id = history_service.create(request, trip_plan)

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            history_id=history_id,
            data=trip_plan
        )

    except sqlite3.Error as e:
        print(f"❌ 历史记录保存失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="旅行计划保存失败，请稍后重试"
        ) from e
    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        agents = [
            agent.attraction_agent,
            agent.weather_agent,
            agent.hotel_agent,
            agent.planner_agent
        ]
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agents_count": len(agents),
            "tools_count": sum(len(item.list_tools()) for item in agents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
