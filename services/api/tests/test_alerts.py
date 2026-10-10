"""Tests for alerts and notifications endpoints."""

from fastapi.testclient import TestClient


def test_list_alerts(client: TestClient) -> None:
    """Verify listing all alerts."""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) >= 5


def test_filter_alerts_by_severity(client: TestClient) -> None:
    """Verify filtering alerts by severity."""
    response = client.get("/api/v1/alerts?severity=critical")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    for alert in json_data["data"]:
        assert alert["severity"] == "critical"


def test_acknowledge_alert_success(client: TestClient) -> None:
    """Verify acknowledging an existing alert."""
    response = client.patch("/api/v1/alerts/alert-01/acknowledge")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["acknowledged"] is True


def test_acknowledge_alert_not_found(client: TestClient) -> None:
    """Verify 404 response on unknown alert ID."""
    response = client.patch("/api/v1/alerts/unknown-alert/acknowledge")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "ALERT_NOT_FOUND"
