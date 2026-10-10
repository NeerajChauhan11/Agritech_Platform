"""Tests for farm and field endpoints."""

from fastapi.testclient import TestClient


def test_list_farms(client: TestClient) -> None:
    """Verify list farms returns demo farm with fields."""
    response = client.get("/api/v1/farms")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) >= 1
    assert json_data["data"][0]["id"] == "farm-alpha"


def test_get_farm_detail_success(client: TestClient) -> None:
    """Verify farm details by ID."""
    response = client.get("/api/v1/farms/farm-alpha")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "farm-alpha"


def test_get_farm_not_found(client: TestClient) -> None:
    """Verify 404 error envelope when farm does not exist."""
    response = client.get("/api/v1/farms/non-existent-farm")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "FARM_NOT_FOUND"


def test_get_field_detail(client: TestClient) -> None:
    """Verify field details endpoint."""
    response = client.get("/api/v1/farms/farm-alpha/fields/field-01")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "field-01"
    assert json_data["data"]["crop"] == "Tomato"
