"""Alerts and notification router."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.alerts import Alert, AlertAcknowledgeResponse
from app.schemas.common import ApiResponse
from app.services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=ApiResponse[list[Alert]])
async def list_alerts(
    field_id: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> ApiResponse[list[Alert]]:
    """Query alerts with optional field, severity, and category filtering."""
    alerts = await alert_service.get_alerts(
        field_id=field_id,
        severity=severity,
        category=category,
    )
    return ApiResponse(success=True, data=alerts)


@router.patch("/{alert_id}/acknowledge", response_model=ApiResponse[AlertAcknowledgeResponse])
async def acknowledge_alert(alert_id: str) -> ApiResponse[AlertAcknowledgeResponse]:
    """Acknowledge a specific agricultural alert."""
    result = await alert_service.acknowledge_alert(alert_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ALERT_NOT_FOUND", "message": f"Alert '{alert_id}' was not found."},
        )
    return ApiResponse(success=True, data=result)
