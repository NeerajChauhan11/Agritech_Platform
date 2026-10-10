"""Tests for yield forecasting endpoints."""

from fastapi.testclient import TestClient


def test_get_yield_predictions(client: TestClient) -> None:
    """Verify fetching all yield predictions."""
    response = client.get("/api/v1/yield/predictions")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) >= 3


def test_get_yield_filtered_by_field(client: TestClient) -> None:
    """Verify filtering yield forecast by field ID."""
    response = client.get("/api/v1/yield/predictions?field_id=field-01")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["field_id"] == "field-01"


def test_predict_yield_post(client: TestClient) -> None:
    """Verify POST yield prediction."""
    payload = {"field_id": "field-02"}
    response = client.post("/api/v1/yield/predict", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"][0]["crop"] == "Apple"


def test_calculate_yield_engine() -> None:
    """Verify algorithmic yield projection calculation."""
    from app.services.yield_service import yield_service

    prediction = yield_service.calculate_yield(
        crop="Tomato",
        field_id="f1",
        field_name="Tomato A",
        moisture=55.0,
        temperature=24.0,
        last_yield=4.5,
    )
    assert prediction.crop == "Tomato"
    assert prediction.estimated_yield_t_per_hectare > 0
    assert prediction.prediction_interval.lower < prediction.estimated_yield_t_per_hectare
    assert prediction.prediction_interval.upper > prediction.estimated_yield_t_per_hectare
    assert len(prediction.factors) == 4

