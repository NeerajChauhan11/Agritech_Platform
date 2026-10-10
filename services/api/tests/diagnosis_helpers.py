"""Shared helpers for diagnosis tests: synthetic images and fake ONNX models."""

from pathlib import Path

import cv2
import numpy as np

from app.core.model_catalog import DISEASE_MODEL_SPECS, ModelSpec
from app.services.crop_identifier import CropIdentification
from app.services.disease_model_registry import DiseaseModelRegistry

CROPS = tuple(DISEASE_MODEL_SPECS)


def encode_png(image: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    assert ok
    return buf.tobytes()


def sharp_leaf_bytes(seed: int = 0) -> bytes:
    """Textured, well-exposed green image that passes the quality gate."""
    rng = np.random.default_rng(seed)
    base = np.full((384, 384, 3), (40, 150, 60), np.uint8)
    noise = rng.normal(0, 28, base.shape)
    return encode_png(np.clip(base + noise, 0, 255).astype(np.uint8))


def blurry_leaf_bytes() -> bytes:
    img = cv2.imdecode(np.frombuffer(sharp_leaf_bytes(), np.uint8), cv2.IMREAD_COLOR)
    return encode_png(cv2.GaussianBlur(img, (0, 0), 25))


def dark_leaf_bytes() -> bytes:
    img = cv2.imdecode(np.frombuffer(sharp_leaf_bytes(), np.uint8), cv2.IMREAD_COLOR)
    return encode_png((img * 0.1).astype(np.uint8))


def probs_peaked(n: int, index: int, peak: float) -> np.ndarray:
    """Probability vector with `peak` at `index`, the remainder spread evenly."""
    probs = np.full(n, (1.0 - peak) / (n - 1), np.float32)
    probs[index] = peak
    return probs


class FakeIdentifier:
    """Crop identifier returning a fixed ranking and recording its calls."""

    def __init__(self, ranked: list[tuple[str, float]]) -> None:
        self.ranked = ranked
        self.calls = 0

    def identify(self, _image: np.ndarray) -> CropIdentification:
        self.calls += 1
        return CropIdentification(True, self.ranked)


class FakeGeneral:
    """General-category classifier stand-in returning a fixed ranking and recording its calls."""

    def __init__(self, ranked: list[tuple[str, float]] | None = None) -> None:
        self.ranked = ranked
        self.calls: list[str] = []

    def is_installed(self) -> bool:
        return self.ranked is not None

    def version(self) -> str:
        return "fake-clip-1"

    def classify(self, _image: np.ndarray, crop: str) -> list[tuple[str, float]]:
        assert self.ranked is not None
        self.calls.append(crop)
        return self.ranked


class FakeModel:
    """Stand-in for OnnxImageClassifier that peaks at a chosen class."""

    def __init__(self, spec: ModelSpec, index: int, peak: float) -> None:
        self.spec = spec
        self._index = min(index, len(spec.classes) - 1)
        self._peak = peak

    def predict(self, _image: np.ndarray) -> np.ndarray:
        return probs_peaked(len(self.spec.classes), self._index, self._peak)


class RegistryRig:
    """A real DiseaseModelRegistry over a temp dir with fake model factories."""

    def __init__(self, models_dir: Path, installed: tuple[str, ...], index: int = 0, peak: float = 0.9) -> None:
        self.loaded: list[str] = []
        self.index = index
        self.peak = peak
        for crop in installed:
            (models_dir / DISEASE_MODEL_SPECS[crop].weights_file).write_bytes(b"x")
        self.registry = DiseaseModelRegistry(
            model_factory=self._factory, models_dir=str(models_dir)
        )

    def _factory(self, spec: ModelSpec, _models_dir: str | None) -> FakeModel:
        self.loaded.append(spec.key)
        return FakeModel(spec, self.index, self.peak)
