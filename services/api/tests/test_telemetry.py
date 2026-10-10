"""Tests for telemetry endpoints."""

from fastapi.testclient import TestClient


def test_get_telemetry_history(client: TestClient) -> None:
    """Verify retrieval of historical telemetry points for field."""
    response = client.get("/api/v1/telemetry/field-01")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 24
    assert "moisture" in json_data["data"][0]


def test_ingest_telemetry(client: TestClient) -> None:
    """Verify ingestion of sensor reading with automated boundary cleaning."""
    payload = {
        "device_id": "esp32-node-01",
        "field_id": "field-01",
        "reading": {
            "timestamp": "2026-10-04T08:00:00Z",
            "soil_moisture": 45.2,
            "temperature": 27.5,
            "humidity": 60.0,
            "ph_level": 6.8,
            "nitrogen": 40.0,
            "phosphorus": 25.0,
            "potassium": 35.0,
        },
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["soil_moisture"] == 45.2


def test_ingest_telemetry_triggers_critical_alert(client: TestClient) -> None:
    """Verify that ingesting telemetry with moisture <= 20% triggers an alert."""
    payload = {
        "device_id": "esp32-node-02",
        "field_id": "field-02",
        "reading": {
            "timestamp": "2026-10-04T09:00:00Z",
            "soil_moisture": 14.5,
            "temperature": 36.5,
            "humidity": 40.0,
            "ph_level": 7.0,
            "nitrogen": 30.0,
            "phosphorus": 20.0,
            "potassium": 25.0,
        },
    }
    client.post("/api/v1/telemetry", json=payload)

    # Check alert endpoint for the critical alert
    alert_resp = client.get("/api/v1/alerts?field_id=field-02&severity=critical")
    assert alert_resp.status_code == 200
    alerts = alert_resp.json()["data"]
    assert any("Depletion" in a["title"] for a in alerts)


def test_telemetry_websocket(client: TestClient) -> None:
    """Verify WebSocket connection and message handshake."""
    with client.websocket_connect("/api/v1/telemetry/ws") as websocket:
        websocket.send_text("ping")
