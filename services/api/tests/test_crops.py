"""Supported-crop scope: normalisation, rejection and absence of silent fallbacks."""

import pytest
from fastapi.testclient import TestClient

from app.core.constants import (
    CROP_ALIASES,
    CROP_PROFILES,
    DIAGNOSIS_STATUS_MESSAGES,
    SUPPORTED_CROPS,
)
from app.core.crops import UnsupportedCropError, normalize_crop, require_supported_crop
from app.demo import fixtures


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("apple", "apple"), ("Tomato", "tomato"), ("  CAPSICUM ", "capsicum"),
        ("pepper", "capsicum"), ("Bell Pepper", "capsicum"), ("bell-pepper", "capsicum"),
        ("Bell_Pepper", "capsicum"), ("sweet pepper", "capsicum"),
    ],
)
def test_supported_crops_and_aliases_normalise(raw: str, expected: str) -> None:
    assert normalize_crop(raw) == expected
    assert require_supported_crop(raw) == expected


@pytest.mark.parametrize(
    "raw", ["wheat", "sugarcane", "Sugar Cane", "rice", "paddy", "potato", "corn", "maize", "", "unknown", "tomatoes"]
)
def test_unsupported_crops_are_rejected(raw: str) -> None:
    assert normalize_crop(raw) is None
    with pytest.raises(UnsupportedCropError, match="apple, tomato, capsicum"):
        require_supported_crop(raw)


def test_none_is_not_a_crop() -> None:
    assert normalize_crop(None) is None


def test_aliases_only_point_at_supported_crops() -> None:
    assert set(CROP_ALIASES.values()) <= set(SUPPORTED_CROPS)
    assert not set(CROP_ALIASES) & set(SUPPORTED_CROPS)  # canonical ids are never aliases


def test_unsupported_status_message_lists_exactly_the_supported_crops() -> None:
    _, action = DIAGNOSIS_STATUS_MESSAGES["crop_unsupported"]
    assert action == "Supported crops: Apple, Tomato, Capsicum."


def test_demo_fixtures_only_use_supported_crops() -> None:
    crops = {f.crop for f in fixtures.DEMO_FARM.fields}
    crops |= {r.crop for r in fixtures.DEMO_IRRIGATION} | {p.crop for p in fixtures.DEMO_YIELD}
    assert crops, "fixtures must not be empty"
    assert None not in {normalize_crop(c) for c in crops}


@pytest.mark.parametrize("crop", ["wheat", "rice", "sugarcane", "potato", "dragonfruit"])
def test_advisors_do_not_fall_back_to_tomato(crop: str) -> None:
    from app.services.irrigation_service import irrigation_service
    from app.services.yield_service import yield_service

    with pytest.raises(UnsupportedCropError):
        irrigation_service.evaluate_irrigation("f", "F", crop, 30.0, 25.0, 60.0)
    with pytest.raises(UnsupportedCropError):
        yield_service.calculate_yield(crop, "f", "F", 50.0, 25.0, 4.0)


@pytest.mark.parametrize("crop", SUPPORTED_CROPS)
def test_advisors_accept_every_supported_crop(crop: str) -> None:
    from app.services.irrigation_service import irrigation_service
    from app.services.yield_service import yield_service

    assert CROP_PROFILES[crop]["moisture_min"] > 0
    assert irrigation_service.evaluate_irrigation("f", "F", crop, 30.0, 25.0, 60.0).crop == crop
    assert yield_service.calculate_yield(crop, "f", "F", 50.0, 25.0, 4.0).crop == crop


def test_yield_predict_rejects_unsupported_crop(client: TestClient) -> None:
    response = client.post("/api/v1/yield/predict", json={"field_id": "field-02", "crop": "wheat"})
    body = response.json()
    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"]["code"] == "CROP_NOT_SUPPORTED"


def test_yield_predict_accepts_supported_crop_alias(client: TestClient) -> None:
    response = client.post("/api/v1/yield/predict", json={"field_id": "field-03", "crop": "pepper"})
    assert response.status_code == 200
    assert response.json()["data"][0]["crop"] == "Capsicum"
