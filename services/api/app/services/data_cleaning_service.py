"""Reusable data cleaning, sanitization, and normalization service."""

import math
from datetime import datetime, timezone
from typing import Any

from app.core.constants import SENSOR_BOUNDS
from app.schemas.telemetry import SensorReading


class DataCleaningService:
    """Authoritative reusable service for data sanitization and boundary checks."""

    @staticmethod
    def sanitize_float(
        value: Any,
        metric_name: str,
        default_fallback: float | None = None,
    ) -> float:
        """Validate, cast, and clip a numeric metric to its physical bounds."""
        bounds = SENSOR_BOUNDS.get(metric_name, {"min": -1000.0, "max": 1000.0, "default": 0.0})
        default_val = default_fallback if default_fallback is not None else bounds["default"]

        if value is None:
            return default_val

        try:
            val = float(value)
        except (ValueError, TypeError):
            return default_val

        if math.isnan(val) or math.isinf(val):
            return default_val

        return max(bounds["min"], min(bounds["max"], val))

    @classmethod
    def clean_sensor_reading(cls, raw: dict[str, Any] | SensorReading) -> SensorReading:
        """Sanitize raw incoming sensor payload against agronomic constraints."""
        data = raw.model_dump() if isinstance(raw, SensorReading) else dict(raw)

        timestamp_val = data.get("timestamp")
        cleaned_timestamp = cls.normalize_timestamp(timestamp_val)

        return SensorReading(
            timestamp=cleaned_timestamp,
            soil_moisture=cls.sanitize_float(data.get("soil_moisture"), "soil_moisture"),
            temperature=cls.sanitize_float(data.get("temperature"), "temperature"),
            humidity=cls.sanitize_float(data.get("humidity"), "humidity"),
            ph_level=cls.sanitize_float(data.get("ph_level"), "ph_level"),
            nitrogen=cls.sanitize_float(data.get("nitrogen"), "nitrogen"),
            phosphorus=cls.sanitize_float(data.get("phosphorus"), "phosphorus"),
            potassium=cls.sanitize_float(data.get("potassium"), "potassium"),
        )

    @staticmethod
    def normalize_timestamp(ts: Any) -> str:
        """Standardize incoming timestamps to ISO 8601 UTC strings."""
        if not ts:
            return datetime.now(timezone.utc).isoformat()
        if isinstance(ts, datetime):
            return ts.astimezone(timezone.utc).isoformat()
        try:
            parsed = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).isoformat()
        except (ValueError, TypeError):
            return datetime.now(timezone.utc).isoformat()


data_cleaner = DataCleaningService()
