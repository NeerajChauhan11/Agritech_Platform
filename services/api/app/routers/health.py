"""Health check endpoint for service observability."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import ApiResponse, HealthData

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[HealthData])
async def check_health() -> ApiResponse[HealthData]:
    """Check service health and demo mode state."""
    data = HealthData(
        status="healthy",
        version=settings.VERSION,
        demo_mode=settings.DEMO_MODE,
        environment=settings.ENVIRONMENT,
    )
    return ApiResponse(success=True, data=data)
