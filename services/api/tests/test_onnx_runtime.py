"""Exercises the real ONNX Runtime path with hand-built tiny models (no fakes)."""

import json
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.model_catalog import CROP_ID_SPEC, DISEASE_MODEL_SPECS
from app.services.crop_identifier import CropIdentifier
from app.services.disease_model_registry import DiseaseModelRegistry
from app.services.onnx_model import (
    ModelRuntimeError,
    OnnxImageClassifier,
    installed_version,
)
from tests.diagnosis_helpers import encode_png
from tests.onnx_builder import write_onnx

pytest.importorskip("onnxruntime")

TOMATO = DISEASE_MODEL_SPECS["tomato"]
RED_CHANNEL = 0


def _reddish_bgr() -> np.ndarray:
    """BGR image whose RGB red channel is high (and blue low)."""
    return np.full((300, 300, 3), (30, 90, 230), np.uint8)


def _leafy_png() -> bytes:
    """Noisy yellow-green leaf: passes the quality gate and has a strong red channel."""
    rng = np.random.default_rng(1)
    base = np.full((384, 384, 3), (30, 170, 215), np.float32)
    return encode_png(np.clip(base + rng.normal(0, 28, base.shape), 0, 255).astype(np.uint8))


def test_classifier_reads_rgb_channels_in_the_right_order(tmp_path: Path) -> None:
    peak = TOMATO.classes.index("late_blight")
    write_onnx(tmp_path / TOMATO.weights_file, len(TOMATO.classes), peak, RED_CHANNEL)
    probs = OnnxImageClassifier(TOMATO, str(tmp_path)).predict(_reddish_bgr())
    assert int(np.argmax(probs)) == peak
    assert float(probs.sum()) == pytest.approx(1.0, abs=1e-5)
    assert float(probs[peak]) > 0.9


def test_registry_ranks_classes_from_the_real_model(tmp_path: Path) -> None:
    peak = TOMATO.classes.index("yellow_leaf_curl_virus")
    write_onnx(tmp_path / TOMATO.weights_file, len(TOMATO.classes), peak, RED_CHANNEL)
    registry = DiseaseModelRegistry(models_dir=str(tmp_path))
    assert registry.availability("tomato") == "available"
    assert registry.availability("capsicum") == "weights_missing"
    assert not registry.has_crop("sugarcane")  # out of scope: not a registry crop at all
    ranked = registry.predict("tomato", _reddish_bgr())
    assert ranked[0][0] == "yellow_leaf_curl_virus"
    assert len(ranked) == len(TOMATO.classes)


def test_wrong_class_count_is_rejected(tmp_path: Path) -> None:
    write_onnx(tmp_path / TOMATO.weights_file, num_classes=3, peak_class=0)
    with pytest.raises(ModelRuntimeError, match="outputs 3 classes"):
        OnnxImageClassifier(TOMATO, str(tmp_path))


def test_sidecar_class_mismatch_is_rejected_and_version_is_read(tmp_path: Path) -> None:
    write_onnx(tmp_path / TOMATO.weights_file, len(TOMATO.classes), 0)
    meta = tmp_path / "disease_tomato.meta.json"
    meta.write_text(json.dumps({"version": "2026.1", "classes": ["a", "b"]}), encoding="utf-8")
    assert installed_version(TOMATO, str(tmp_path)) == "2026.1"
    with pytest.raises(ModelRuntimeError, match="does not match"):
        OnnxImageClassifier(TOMATO, str(tmp_path))


def test_corrupt_weights_report_model_unavailable_not_a_crash(tmp_path: Path) -> None:
    (tmp_path / TOMATO.weights_file).write_bytes(b"not an onnx file")
    registry = DiseaseModelRegistry(models_dir=str(tmp_path))
    with pytest.raises(ModelRuntimeError):
        registry.predict("tomato", _reddish_bgr())


def test_full_pipeline_with_real_onnx_models(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    crop_peak = CROP_ID_SPEC.classes.index("tomato")
    disease_peak = TOMATO.classes.index("late_blight")
    write_onnx(tmp_path / CROP_ID_SPEC.weights_file, len(CROP_ID_SPEC.classes), crop_peak, RED_CHANNEL)
    write_onnx(tmp_path / TOMATO.weights_file, len(TOMATO.classes), disease_peak, RED_CHANNEL)
    monkeypatch.setattr(settings, "AI_MODEL_PATH", str(tmp_path))
    from app.services.diagnosis_service import diagnosis_service

    monkeypatch.setattr(diagnosis_service, "identifier", CropIdentifier())
    monkeypatch.setattr(diagnosis_service, "registry", DiseaseModelRegistry())

    files = {"file": ("leaf.png", BytesIO(_leafy_png()), "image/png")}
    data = client.post("/api/v1/diagnose", files=files).json()["data"]

    assert data["status"] == "ok"
    assert data["detected_crop"] == "Tomato"
    assert data["disease_label"] == "late_blight"
    assert data["crop_confidence"] > 0.9 and data["disease_confidence"] > 0.9
