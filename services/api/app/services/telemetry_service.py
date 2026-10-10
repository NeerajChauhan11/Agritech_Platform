"""Service for sensor telemetry retrieval, ingestion, and real-time streaming."""

from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.demo import fixtures
from app.schemas.telemetry import SensorReading, TelemetryIngestPayload, TelemetryPoint
from app.services.alert_service import alert_service
from app.services.data_cleaning_service import data_cleaner


class TelemetryService:
    """Telemetry retrieval, ingestion, and real-time distribution coordinator."""

    def __init__(self) -> None:
        self._history: dict[str, list[TelemetryPoint]] = defaultdict(
            list,
            {k: list(v) for k, v in fixtures.DEMO_TELEMETRY.items()},
        )
        self._active_connections: list[WebSocket] = []

    async def register_connection(self, websocket: WebSocket) -> None:
        """Register active WebSocket for live telemetry stream."""
        await websocket.accept()
        self._active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Unregister closed WebSocket."""
        if websocket in self._active_connections:
            self._active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast live telemetry frame to all connected subscribers."""
        dead_connections = []
        for connection in self._active_connections:
            try:
                await connection.send_json(message)
            except (RuntimeError, WebSocketDisconnect):
                dead_connections.append(connection)
        for dc in dead_connections:
            self.disconnect(dc)

    async def get_history(self, field_id: str) -> list[TelemetryPoint]:
        """Fetch 24h historical telemetry points for a given field."""
        if field_id in self._history:
            return self._history[field_id]
        if settings.DEMO_MODE:
            return fixtures.DEMO_TELEMETRY.get("field-01", [])
        return []

    async def ingest(self, payload: TelemetryIngestPayload) -> SensorReading:
        """Sanitize raw incoming IoT telemetry, evaluate alerts, and broadcast."""
        cleaned = data_cleaner.clean_sensor_reading(payload.reading)
        await alert_service.evaluate_reading(payload.device_id, payload.field_id, cleaned)

        # Append to live history
        new_point = TelemetryPoint(
            time=cleaned.timestamp[-8:-3] if len(cleaned.timestamp) >= 8 else "now",
            moisture=cleaned.soil_moisture,
            temperature=cleaned.temperature,
            humidity=cleaned.humidity,
            ph=cleaned.ph_level,
        )
        field_points = self._history[payload.field_id]
        field_points.append(new_point)
        if len(field_points) > 48:
            field_points.pop(0)

        # Live push
        await self.broadcast({"type": "telemetry", "field_id": payload.field_id, "data": cleaned.model_dump()})
        return cleaned


telemetry_service = TelemetryService()
