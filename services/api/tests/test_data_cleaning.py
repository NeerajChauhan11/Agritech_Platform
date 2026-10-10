"""Unit tests for the reusable data cleaning and sanitization service."""

from app.services.data_cleaning_service import data_cleaner


def test_sanitize_float_clipping() -> None:
    """Verify out-of-range sensor values are clipped to physical bounds."""
    # Soil moisture bounds are [0, 100]
    assert data_cleaner.sanitize_float(150.0, "soil_moisture") == 100.0
    assert data_cleaner.sanitize_float(-25.0, "soil_moisture") == 0.0
    assert data_cleaner.sanitize_float(45.5, "soil_moisture") == 45.5


def test_sanitize_float_invalid_values() -> None:
    """Verify NaN, None, and unparseable strings fall back to agronomic defaults."""
    default_moisture = 45.0
    assert data_cleaner.sanitize_float(None, "soil_moisture") == default_moisture
    assert data_cleaner.sanitize_float(float("nan"), "soil_moisture") == default_moisture
    assert data_cleaner.sanitize_float("not_a_number", "soil_moisture") == default_moisture


def test_clean_sensor_reading_pipeline() -> None:
    """Verify the entire clean-drive pipeline cleans dirty telemetry."""
    dirty_payload = {
        "timestamp": "2026-10-04 08:30:00",
        "soil_moisture": 120.0,  # exceeds max
        "temperature": 999.0,   # exceeds max
        "humidity": -5.0,       # below min
        "ph_level": 7.1,
        "nitrogen": "invalid",  # invalid type
        "phosphorus": None,     # missing
        "potassium": 38.0,
    }

    cleaned = data_cleaner.clean_sensor_reading(dirty_payload)
    assert cleaned.soil_moisture == 100.0
    assert cleaned.temperature == 65.0
    assert cleaned.humidity == 0.0
    assert cleaned.ph_level == 7.1
    assert cleaned.nitrogen == 40.0  # default
    assert cleaned.phosphorus == 25.0  # default
    assert cleaned.potassium == 38.0
