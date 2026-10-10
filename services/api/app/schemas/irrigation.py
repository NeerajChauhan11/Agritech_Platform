"""Schemas for precision irrigation recommendations and confirmations."""

from typing import Literal

from pydantic import BaseModel, Field


class SensorSnapshot(BaseModel):
    """Snapshot of telemetry values relevant to irrigation."""

    soil_moisture: float
    temperature: float
    humidity: float


class IrrigationRecommendation(BaseModel):
    """Agronomic recommendation for field irrigation."""

    field_id: str
    field_name: str
    crop: str
    water_stress: Literal["low", "medium", "high", "critical"]
    irrigation_required: bool
    estimated_duration_minutes: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str]
    sensor_snapshot: SensorSnapshot


class IrrigationConfirmRequest(BaseModel):
    """Farmer confirmation of irrigation cycle."""

    field_id: str
    duration_minutes: int | None = None


class IrrigationConfirmResponse(BaseModel):
    """Outcome acknowledgment of the irrigation cycle."""

    field_id: str
    status: str
    message: str
    confirmed_at: str
