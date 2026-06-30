"""旅行历史API路由"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ...models.schemas import (
    TripHistoryDetailResponse,
    TripHistoryListResponse,
    TripHistoryUpdateRequest,
)
from ...services.trip_history_service import (
    TripHistoryService,
    get_trip_history_service,
)


router = APIRouter(prefix="/history", tags=["旅行历史"])
DATABASE_ERROR_MESSAGE = "历史记录服务暂时不可用"


def get_history_service() -> TripHistoryService:
    """获取旅行历史服务，允许测试通过依赖覆盖替换。"""
    return get_trip_history_service()


@router.get("", response_model=TripHistoryListResponse)
def list_history(
    service: TripHistoryService = Depends(get_history_service),
):
    try:
        return TripHistoryListResponse(
            success=True,
            message="获取历史记录成功",
            data=service.list(),
        )
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=DATABASE_ERROR_MESSAGE,
        ) from exc


@router.get("/{history_id}", response_model=TripHistoryDetailResponse)
def get_history(
    history_id: str,
    service: TripHistoryService = Depends(get_history_service),
):
    try:
        history = service.get(history_id)
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=DATABASE_ERROR_MESSAGE,
        ) from exc

    if history is None:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return TripHistoryDetailResponse(
        success=True,
        message="获取历史记录成功",
        data=history,
    )


@router.put("/{history_id}", response_model=TripHistoryDetailResponse)
def update_history(
    history_id: str,
    request: TripHistoryUpdateRequest,
    service: TripHistoryService = Depends(get_history_service),
):
    try:
        updated = service.update(history_id, request.plan)
        history = service.get(history_id) if updated else None
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=DATABASE_ERROR_MESSAGE,
        ) from exc

    if history is None:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return TripHistoryDetailResponse(
        success=True,
        message="更新历史记录成功",
        data=history,
    )


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_history(
    history_id: str,
    service: TripHistoryService = Depends(get_history_service),
):
    try:
        deleted = service.delete(history_id)
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=DATABASE_ERROR_MESSAGE,
        ) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
