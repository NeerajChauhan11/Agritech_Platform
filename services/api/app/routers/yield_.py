"""Yield forecasting router."""

from fastapi import APIRouter, Query

from app.core.crops import require_supported_crop
from app.schemas.common import ApiResponse
from app.schemas.yield_ import YieldPrediction, YieldPredictRequest
from app.services.yield_service import yield_service

router = APIRouter(prefix="/yield", tags=["Yield Prediction"])


@router.get("/predictions", response_model=ApiResponse[list[YieldPrediction]])
async def get_yield_forecasts(
    field_id: str | None = Query(default=None, description="Optional field ID filter"),
) -> ApiResponse[list[YieldPrediction]]:
    """Retrieve yield forecasts for fields."""
    predictions = await yield_service.get_yield_predictions(field_id=field_id)
    return ApiResponse(success=True, data=predictions)


@router.post("/predict", response_model=ApiResponse[list[YieldPrediction]])
async def predict_yield(
    request: YieldPredictRequest,
) -> ApiResponse[list[YieldPrediction]]:
    """Calculate yield forecast for given field parameters."""
    if request.crop is not None:
        require_supported_crop(request.crop)
    predictions = await yield_service.get_yield_predictions(field_id=request.field_id)
    return ApiResponse(success=True, data=predictions)
