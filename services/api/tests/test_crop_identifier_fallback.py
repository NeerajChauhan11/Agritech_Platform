"""Crop identification uses a trained model if installed, else labelled zero-shot CLIP."""

from pathlib import Path

import numpy as np

from app.core.model_catalog import CROP_ID_SPEC
from app.services.crop_identifier import CropIdentifier
from tests.diagnosis_helpers import probs_peaked

IMAGE = np.zeros((8, 8, 3), np.uint8)


class FakeZeroShot:
    def __init__(self, installed: bool = True) -> None:
        self.installed = installed

    def is_installed(self) -> bool:
        return self.installed

    def group_probabilities(self, _bgr, groups):
        names = list(groups)
        return [(names[1], 0.8), (names[0], 0.2)]


class FakeTrained:
    def __init__(self, spec, _dir) -> None:
        self.spec = spec

    def predict(self, _bgr):
        return probs_peaked(len(self.spec.classes), 0, 0.9)


def test_zero_shot_fallback_is_labelled(tmp_path: Path) -> None:
    result = CropIdentifier(models_dir=str(tmp_path), zero_shot=FakeZeroShot()).identify(IMAGE)
    assert result.available and result.method == "zero_shot_clip"
    assert result.candidates[0][1] == 0.8


def test_nothing_installed_is_unavailable(tmp_path: Path) -> None:
    result = CropIdentifier(models_dir=str(tmp_path), zero_shot=FakeZeroShot(False)).identify(IMAGE)
    assert not result.available


def test_trained_model_takes_priority(tmp_path: Path) -> None:
    (tmp_path / CROP_ID_SPEC.weights_file).write_bytes(b"x")
    ident = CropIdentifier(model_factory=FakeTrained, models_dir=str(tmp_path), zero_shot=FakeZeroShot())
    result = ident.identify(IMAGE)
    assert result.available and result.method == "trained_classifier"
