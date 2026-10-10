"""Irrigation advisor and confirmation router."""

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.irrigation import (
    IrrigationConfirmRequest,
    IrrigationConfirmResponse,
    IrrigationRecommendation,
)
from app.services.irrigation_service import irrigation_service

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


@router.get("/recommendations", response_model=ApiResponse[list[IrrigationRecommendation]])
async def get_irrigation_recommendations() -> ApiResponse[list[IrrigationRecommendation]]:
    """Retrieve current irrigation recommendations for all fields."""
    recs = await irrigation_service.get_recommendations()
    return ApiResponse(success=True, data=recs)


@router.post("/confirm", response_model=ApiResponse[IrrigationConfirmResponse])
async def confirm_irrigation_cycle(
    request: IrrigationConfirmRequest,
) -> ApiResponse[IrrigationConfirmResponse]:
    """Record confirmation of an irrigation cycle by the grower."""
    response = await irrigation_service.confirm_irrigation(request)
    return ApiResponse(success=True, data=response)
