"""Schemas for farm, field, and device representations."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.telemetry import SensorReading


class Device(BaseModel):
    """IoT sensor edge device representation."""

    id: str
    name: str
    field_id: str
    status: Literal["online", "offline", "warning"]
    last_seen: str
    battery: float = Field(..., ge=0, le=100)
    signal: float = Field(..., ge=0, le=100)


class FieldSchema(BaseModel):
    """Agricultural field partition inside a farm."""

    id: str
    name: str
    farm_id: str
    crop: str
    area_hectares: float = Field(..., gt=0)
    health_score: float = Field(..., ge=0, le=100)
    status: Literal["healthy", "warning", "critical"]
    growth_stage: str
    devices: list[Device]
    latest_reading: SensorReading
    coordinates: tuple[float, float] = Field(..., description="[lat, lng]")


class Farm(BaseModel):
    """Comprehensive agricultural enterprise schema."""

    id: str
    name: str
    location: str
    total_area_hectares: float = Field(..., gt=0)
    fields: list[FieldSchema]
    overall_health: float = Field(..., ge=0, le=100)
