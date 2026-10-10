"""Tests for the general-category tier (zero-shot CLIP) and its selection against specific models."""

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.constants import SUPPORTED_CROPS
from app.core.general_catalog import GENERAL_CATEGORIES, GENERAL_TIER_NOTICE
from app.core.model_catalog import DISEASE_MODEL_SPECS
from app.knowledge.general_categories import get_category_guidance
from app.services.diagnosis_service import diagnosis_service
from tests.diagnosis_helpers import (
    FakeGeneral,
    FakeIdentifier,
    RegistryRig,
    blurry_leaf_bytes,
    sharp_leaf_bytes,
)

CONFIDENT_FUNGAL = [("fungal", 0.80), ("bacterial", 0.10), ("healthy", 0.10)]


def _diagnose(client: TestClient, image: bytes) -> dict:
    files = {"file": ("leaf.png", BytesIO(image), "image/png")}
    response = client.post("/api/v1/diagnose", files=files)
    assert response.status_code == 200
    return response.json()["data"]


def _crop(crop: str) -> list[tuple[str, float]]:
    return [(crop, 0.93), ("unknown", 0.04), ("apple" if crop != "apple" else "tomato", 0.03)]


@pytest.fixture
def tiers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Fake crop ID, fake general classifier, and specific models installed only where asked."""

    def build(crop_ranking, general_ranked=CONFIDENT_FUNGAL, specific=()):
        general = FakeGeneral(general_ranked)
        rigged = RegistryRig(tmp_path, specific)
        monkeypatch.setattr(diagnosis_service, "identifier", FakeIdentifier(crop_ranking))
        monkeypatch.setattr(diagnosis_service, "registry", rigged.registry)
        monkeypatch.setattr(diagnosis_service, "general", general)
        return general, rigged

    return build


@pytest.mark.parametrize("crop", SUPPORTED_CROPS)
def test_general_tier_used_when_no_specific_model(client: TestClient, tiers, crop: str) -> None:
    general, rigged = tiers(_crop(crop))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "ok"
    assert data["detected_crop"] == crop.capitalize()
    assert data["diagnosis_tier"] == "general_category"
    assert data["tier_notice"] == GENERAL_TIER_NOTICE
    assert data["category"]["id"] == "fungal"
    assert data["category"]["label"] == GENERAL_CATEGORIES["fungal"]
    assert [c["label"] for c in data["category_predictions"]] == ["fungal", "bacterial", "healthy"]
    assert data["symptoms"] and data["recommendations"]["treatment"]
    assert general.calls == [crop]
    assert rigged.loaded == []


def test_general_result_makes_no_specific_disease_claim(client: TestClient, tiers) -> None:
    tiers(_crop("tomato"))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["disease_name"] is None and data["disease_label"] is None
    assert data["predictions"] == [] and data["severity"] is None
    headline = f"{data['message']} {data['category']['label']}".lower()
    for spec in DISEASE_MODEL_SPECS.values():
        for label in spec.classes:
            if label != "healthy":
                assert label.replace("_", " ") not in headline


def test_specific_model_wins_over_general_when_installed(client: TestClient, tiers) -> None:
    general, rigged = tiers(_crop("tomato"), specific=("tomato",))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "ok"
    assert data["diagnosis_tier"] == "specific"
    assert data["tier_notice"] is None and data["category"] is None
    assert data["disease_label"] in DISEASE_MODEL_SPECS["tomato"].classes
    assert rigged.loaded == ["tomato"]
    assert general.calls == []


def test_other_crops_missing_model_still_uses_general(client: TestClient, tiers) -> None:
    general, rigged = tiers(_crop("capsicum"), specific=("tomato",))
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["diagnosis_tier"] == "general_category"
    assert rigged.loaded == [] and general.calls == ["capsicum"]


@pytest.mark.parametrize(
    "ranked",
    [
        [("fungal", 0.40), ("bacterial", 0.30), ("healthy", 0.30)],  # below confidence minimum
        [("fungal", 0.55), ("bacterial", 0.45)],  # too close to the runner-up
    ],
)
def test_low_category_confidence_is_disease_uncertain(client: TestClient, tiers, ranked) -> None:
    tiers(_crop("apple"), general_ranked=ranked)
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "disease_uncertain"
    assert data["diagnosis_tier"] == "general_category"
    assert data["tier_notice"] == GENERAL_TIER_NOTICE
    assert data["category"] is None and data["recommendations"] is None
    assert data["category_predictions"]


def test_healthy_category_message(client: TestClient, tiers) -> None:
    tiers(_crop("apple"), general_ranked=[("healthy", 0.9), ("fungal", 0.1)])
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["category"]["id"] == "healthy"
    assert "no clear disease signs" in data["message"]


def test_general_unavailable_without_specific_is_model_unavailable(client: TestClient, tiers) -> None:
    tiers(_crop("tomato"), general_ranked=None)
    data = _diagnose(client, sharp_leaf_bytes())
    assert data["status"] == "model_unavailable"
    assert data["diagnosis_tier"] is None and data["category"] is None


def test_gates_run_before_the_general_tier(client: TestClient, tiers) -> None:
    general, _ = tiers(_crop("tomato"))
    blurry = _diagnose(client, blurry_leaf_bytes())
    assert blurry["status"] == "low_quality_image" and blurry["diagnosis_tier"] is None

    general, _ = tiers(_crop("wheat"))
    unsupported = _diagnose(client, sharp_leaf_bytes())
    assert unsupported["status"] == "crop_unsupported" and unsupported["diagnosis_tier"] is None

    general_b, _ = tiers([("unknown", 0.9), ("tomato", 0.06), ("apple", 0.04)])
    assert _diagnose(client, sharp_leaf_bytes())["status"] == "crop_uncertain"
    assert general.calls == [] and general_b.calls == []


def test_models_endpoint_reports_general_tier(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(diagnosis_service, "general", FakeGeneral(CONFIDENT_FUNGAL))
    models = {m["model"]: m for m in client.get("/api/v1/diagnose/models").json()["data"]}
    assert models["general_category"]["status"] == "available"
    assert models["general_category"]["classes"] == list(GENERAL_CATEGORIES)


@pytest.mark.parametrize("crop", SUPPORTED_CROPS)
def test_every_crop_category_has_plain_guidance(crop: str) -> None:
    for category in GENERAL_CATEGORIES:
        guidance = get_category_guidance(crop, category)
        assert guidance and guidance.look_for and guidance.actions and guidance.consult
        text = " ".join([guidance.description, *guidance.actions, *guidance.prevention])
        assert not any(ch.isdigit() for ch in text)  # no dosages or rates
