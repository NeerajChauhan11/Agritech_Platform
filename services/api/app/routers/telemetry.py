"""Telemetry ingestion and query router."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.common import ApiResponse
from app.schemas.telemetry import SensorReading, TelemetryIngestPayload, TelemetryPoint
from app.services.telemetry_service import telemetry_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.get("/{field_id}", response_model=ApiResponse[list[TelemetryPoint]])
async def get_field_telemetry(field_id: str) -> ApiResponse[list[TelemetryPoint]]:
    """Retrieve 24-hour telemetry history for a field."""
    points = await telemetry_service.get_history(field_id)
    return ApiResponse(success=True, data=points)


@router.post("", response_model=ApiResponse[SensorReading])
async def ingest_sensor_reading(payload: TelemetryIngestPayload) -> ApiResponse[SensorReading]:
    """Ingest new sensor reading through the automated data cleaning pipeline."""
    cleaned = await telemetry_service.ingest(payload)
    return ApiResponse(success=True, data=cleaned)


@router.websocket("/ws")
async def telemetry_websocket(websocket: WebSocket) -> None:
    """Live WebSocket feed for real-time telemetry streaming."""
    await telemetry_service.register_connection(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_service.disconnect(websocket)
