"""Tests for irrigation endpoints."""

from fastapi.testclient import TestClient


def test_get_irrigation_recommendations(client: TestClient) -> None:
    """Verify list of irrigation recommendations."""
    response = client.get("/api/v1/irrigation/recommendations")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 4


def test_confirm_irrigation(client: TestClient) -> None:
    """Verify confirming an irrigation cycle."""
    payload = {"field_id": "field-01", "duration_minutes": 15}
    response = client.post("/api/v1/irrigation/confirm", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "scheduled"


def test_evaluate_irrigation_critical_stress() -> None:
    """Verify critical stress assessment when moisture <= 20%."""
    from app.services.irrigation_service import irrigation_service

    rec = irrigation_service.evaluate_irrigation(
        field_id="f1",
        field_name="Tomato A",
        crop="Tomato",
        moisture=15.0,
        temperature=32.0,
        humidity=40.0,
    )
    assert rec.water_stress == "critical"
    assert rec.irrigation_required is True
    assert rec.estimated_duration_minutes == 25


def test_evaluate_irrigation_adequate_moisture() -> None:
    """Verify no irrigation needed when moisture is adequate."""
    from app.services.irrigation_service import irrigation_service

    rec = irrigation_service.evaluate_irrigation(
        field_id="f1",
        field_name="Capsicum P",
        crop="Capsicum",
        moisture=72.0,
        temperature=26.0,
        humidity=75.0,
    )
    assert rec.water_stress == "low"
    assert rec.irrigation_required is False
    assert rec.estimated_duration_minutes == 0

