"""Tests for the automatic crop-ID + crop-specific disease diagnosis pipeline."""

import importlib.util
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.model_catalog import DISEASE_MODEL_SPECS
from app.services.diagnosis_service import diagnosis_service
from tests.diagnosis_helpers import (
    CROPS,
    FakeGeneral,
    FakeIdentifier,
    RegistryRig,
    blurry_leaf_bytes,
    dark_leaf_bytes,
    sharp_leaf_bytes,
)


def _diagnose(client: TestClient, image: bytes, **data: str) -> dict:
    files = {"file": ("leaf.png", BytesIO(image), "image/png")}
    response = client.post("/api/v1/diagnose", files=files, data=data)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    return body["data"]


def _confident(crop: str) -> list[tuple[str, float]]:
    other = next(c for c in CROPS if c != crop)
    return [(crop, 0.93), ("unknown", 0.04), (other, 0.03)]


@pytest.fixture
def rig(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Install fake weights for chosen crops and a fixed crop-ID ranking."""

    def build(crop_ranking, installed=CROPS, index=0, peak=0.9):
        identifier = FakeIdentifier(crop_ranking)
        rigged = RegistryRig(tmp_path, installed, index, peak)
        monkeypatch.setattr(diagnosis_service, "identifier", identifier)
        monkeypatch.setattr(diagnosis_service, "registry", rigged.registry)
        monkeypatch.setattr(diagnosis_service, "general", FakeGeneral())  # general tier not installed
        return rigged

    return build


def test_blurry_image_is_low_quality(client: TestClient) -> None:
    data = _diagnose(client, blurry_leaf_bytes())
    assert data["status"] == "low_quality_image"
    assert "blurry" in data["message"].lower()
    assert data["user_action"]
    assert data["disease_name"] is None
    assert data["predictions"] == []


def test_dark_image_is_low_quality(client: TestClient) -> None:
    data = _diagnose(client, dark_leaf_bytes())
    assert data["status"] == "low_quality_image"
    assert "dark" in data["message"].lower()


def test_non_leaf_image_is_crop_uncertain(client: TestClient, rig) -> None:
    rig([("unknown", 0.91), ("tomato", 0.05), ("apple", 0.04)])
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "crop_uncertain"
    assert data["detected_crop"] is None
    assert data["disease_name"] is None
    assert data["crop_candidates"][0]["label"] == "unknown"
    assert data["user_action"]


def test_ambiguous_crop_margin_is_crop_uncertain(client: TestClient, rig) -> None:
    rig([("tomato", 0.55), ("apple", 0.40), ("unknown", 0.05)])
    assert _diagnose(client, sharp_leaf_bytes())["status"] == "crop_uncertain"


@pytest.mark.parametrize("label", ["cotton", "wheat", "sugarcane", "rice", "potato", "corn"])
def test_unsupported_crop(client: TestClient, rig, label: str) -> None:
    rigged = rig([(label, 0.95), ("unknown", 0.03), ("tomato", 0.02)])
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "crop_unsupported"
    assert data["disease_name"] is None
    assert data["predictions"] == []
    assert rigged.loaded == []  # no model, least of all Tomato's, ran on an unsupported crop
    for crop in ("Apple", "Tomato", "Capsicum"):
        assert crop in data["user_action"]


def test_missing_weights_gives_model_unavailable_and_no_fallback(client: TestClient, rig) -> None:
    rigged = rig(_confident("capsicum"), installed=("tomato",))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "model_unavailable"
    assert data["detected_crop"] == "Capsicum"
    assert data["crop_confidence"] == pytest.approx(0.93)
    assert data["disease_name"] is None
    assert rigged.loaded == []  # the Tomato model was not used as a fallback


def test_no_weights_installed_at_all(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "AI_MODEL_PATH", str(tmp_path))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "model_unavailable"
    assert data["detected_crop"] is None
    assert data["disease_name"] is None


def test_low_confidence_disease_is_uncertain(client: TestClient, rig) -> None:
    rig(_confident("tomato"), peak=0.40)
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "disease_uncertain"
    assert data["disease_name"] is None
    assert data["recommendations"] is None
    assert len(data["predictions"]) == 3
    assert data["disease_confidence"] == pytest.approx(0.4)


def test_happy_path_uses_the_identified_crops_model(client: TestClient, rig) -> None:
    index = DISEASE_MODEL_SPECS["tomato"].classes.index("late_blight")
    rigged = rig(_confident("tomato"), index=index)
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "ok"
    assert data["detected_crop"] == "Tomato"
    assert data["disease_label"] == "late_blight"
    assert data["severity"] == "high"
    assert len(data["predictions"]) == 3
    assert data["symptoms"]
    assert data["recommendations"]["treatment"] and data["recommendations"]["prevention"]
    assert data["model_version"]
    assert rigged.loaded == ["tomato"]


def test_apple_is_never_diagnosed_by_the_tomato_model(client: TestClient, rig) -> None:
    rigged = rig(_confident("apple"), index=1)
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "ok"
    assert data["detected_crop"] == "Apple"
    assert data["disease_label"] in DISEASE_MODEL_SPECS["apple"].classes
    assert data["disease_label"] not in DISEASE_MODEL_SPECS["tomato"].classes
    assert rigged.loaded == ["apple"]


@pytest.mark.parametrize("crop", CROPS)
def test_each_crop_loads_only_its_own_model(client: TestClient, rig, crop: str) -> None:
    rigged = rig(_confident(crop))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "ok"
    assert data["detected_crop"] == crop.capitalize()
    assert data["disease_label"] in DISEASE_MODEL_SPECS[crop].classes
    assert rigged.loaded == [crop]


def test_different_crops_do_not_all_return_tomato_or_early_blight(client: TestClient, rig) -> None:
    results = {}
    for crop in CROPS:
        rig(_confident(crop), index=len(DISEASE_MODEL_SPECS[crop].classes) - 2)
        results[crop] = _diagnose(client, sharp_leaf_bytes())
    assert {r["detected_crop"] for r in results.values()} == {c.capitalize() for c in CROPS}
    assert len({r["disease_label"] for r in results.values()}) == len(CROPS)
    assert all(r["disease_label"] != "early_blight" for r in results.values())
    for crop, result in results.items():
        if crop != "tomato":
            assert "Tomato" not in result["message"]


def test_deprecated_crop_parameter_is_ignored(client: TestClient, rig) -> None:
    rig(_confident("capsicum"))
    data = _diagnose(client, sharp_leaf_bytes(), crop="Tomato")
    assert data["detected_crop"] == "Capsicum"


def test_deprecated_crop_alias_is_accepted(client: TestClient, rig) -> None:
    rig(_confident("capsicum"))
    assert _diagnose(client, sharp_leaf_bytes(), crop="pepper")["detected_crop"] == "Capsicum"


@pytest.mark.parametrize("crop", ["wheat", "Sugarcane", "rice", "paddy", "potato", "dragonfruit"])
def test_unsupported_crop_parameter_is_rejected(client: TestClient, rig, crop: str) -> None:
    rigged = rig(_confident("tomato"))
    files = {"file": ("leaf.png", BytesIO(sharp_leaf_bytes()), "image/png")}
    response = client.post("/api/v1/diagnose", files=files, data={"crop": crop})
    body = response.json()
    assert response.status_code == 400
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "CROP_NOT_SUPPORTED"
    assert "apple, tomato, capsicum" in body["error"]["message"]
    assert rigged.loaded == []  # rejected before any inference


def test_invalid_payload_is_rejected(client: TestClient) -> None:
    files = {"file": ("bad.png", BytesIO(b"definitely not an image header"), "image/png")}
    response = client.post("/api/v1/diagnose", files=files)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_IMAGE_PAYLOAD"


def test_models_endpoint_reports_availability(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "AI_MODEL_PATH", str(tmp_path))
    (tmp_path / DISEASE_MODEL_SPECS["capsicum"].weights_file).write_bytes(b"x")
    response = client.get("/api/v1/diagnose/models")
    models = response.json()["data"]
    status = {m["model"]: m["status"] for m in models}
    assert [m["model"] for m in models] == ["apple", "tomato", "capsicum", "general_category"]
    assert status == {
        "apple": "weights_missing",
        "tomato": "weights_missing",
        "capsicum": "available",
        "general_category": "weights_missing",
    }


def test_colour_heuristic_classifier_is_gone() -> None:
    assert importlib.util.find_spec("app.services.vision_classifier") is None
