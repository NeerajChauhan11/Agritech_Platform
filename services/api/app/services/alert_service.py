"""Service for alert events management and automatic threshold breach alerts."""

import uuid

from app.core.constants import (
    SOIL_MOISTURE_CRITICAL_THRESHOLD,
    TEMP_EXTREME_HEAT_THRESHOLD,
)
from app.demo import fixtures
from app.schemas.alerts import Alert, AlertAcknowledgeResponse
from app.schemas.telemetry import SensorReading


class AlertService:
    """Alert event routing, filtering, threshold evaluation, and acknowledgment."""

    def __init__(self) -> None:
        self._alerts: list[Alert] = list(fixtures.DEMO_ALERTS)

    async def get_alerts(
        self,
        field_id: str | None = None,
        severity: str | None = None,
        category: str | None = None,
    ) -> list[Alert]:
        """Fetch alerts matching criteria."""
        alerts = self._alerts
        filtered = alerts

        if field_id:
            filtered = [a for a in filtered if a.field_id == field_id]
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        if category:
            filtered = [a for a in filtered if a.category == category]

        return filtered

    async def acknowledge_alert(self, alert_id: str) -> AlertAcknowledgeResponse | None:
        """Mark an alert as acknowledged."""
        for a in self._alerts:
            if a.id == alert_id:
                a.acknowledged = True
                return AlertAcknowledgeResponse(
                    id=alert_id,
                    acknowledged=True,
                    message=f"Alert {alert_id} acknowledged successfully.",
                )
        return None

    async def evaluate_reading(
        self,
        device_id: str,
        field_id: str,
        reading: SensorReading,
    ) -> list[Alert]:
        """Evaluate sensor metrics and append alerts if thresholds are breached."""
        new_alerts: list[Alert] = []
        if reading.soil_moisture <= SOIL_MOISTURE_CRITICAL_THRESHOLD:
            alert = Alert(
                id=f"alert-wsi-{uuid.uuid4().hex[:6]}",
                field_id=field_id,
                field_name=f"Field {field_id}",
                category="irrigation",
                severity="critical",
                title="Critical Soil Moisture Depletion",
                message=f"Node {device_id} reported soil moisture at {reading.soil_moisture:.1f}%. Immediate irrigation needed.",
                timestamp=reading.timestamp,
                acknowledged=False,
            )
            self._alerts.insert(0, alert)
            new_alerts.append(alert)

        if reading.temperature >= TEMP_EXTREME_HEAT_THRESHOLD:
            alert = Alert(
                id=f"alert-heat-{uuid.uuid4().hex[:6]}",
                field_id=field_id,
                field_name=f"Field {field_id}",
                category="weather",
                severity="warning",
                title="Extreme Heat Stress",
                message=f"Ambient temperature peaked at {reading.temperature:.1f}°C in field {field_id}.",
                timestamp=reading.timestamp,
                acknowledged=False,
            )
            self._alerts.insert(0, alert)
            new_alerts.append(alert)

        return new_alerts


alert_service = AlertService()
