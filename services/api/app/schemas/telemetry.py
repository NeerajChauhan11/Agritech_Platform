"""Schemas for sensor readings and telemetry data points."""

from datetime import datetime

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """Real-time sensor measurements from an IoT node."""

    timestamp: str = Field(..., description="ISO 8601 formatted timestamp")
    soil_moisture: float = Field(..., ge=0, le=100, description="Volumetric moisture %")
    temperature: float = Field(..., description="Ambient temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    ph_level: float = Field(..., ge=0, le=14, description="Soil pH reading")
    nitrogen: float = Field(..., ge=0, description="Nitrogen content mg/kg")
    phosphorus: float = Field(..., ge=0, description="Phosphorus content mg/kg")
    potassium: float = Field(..., ge=0, description="Potassium content mg/kg")


class TelemetryPoint(BaseModel):
    """Historical or chart telemetry data point."""

    time: str = Field(..., description="Time label or formatted string")
    moisture: float = Field(..., description="Soil moisture percentage")
    temperature: float = Field(..., description="Temperature in °C")
    humidity: float = Field(..., description="Humidity percentage")
    ph: float = Field(..., description="Soil pH value")


class TelemetryIngestPayload(BaseModel):
    """Ingestion contract for IoT edge devices or simulators."""

    device_id: str = Field(..., min_length=1)
    field_id: str = Field(..., min_length=1)
    timestamp: datetime | None = None
    reading: SensorReading
