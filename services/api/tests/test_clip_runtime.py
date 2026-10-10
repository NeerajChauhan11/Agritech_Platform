"""Runs the real CLIP ONNX files on a synthetic image (skipped if the weights are not fetched)."""

import numpy as np
import pytest

from app.core.general_catalog import CLIP_SPEC, CROP_ID_PROMPTS
from app.services.clip_runtime import ClipEncoder
from app.services.clip_tokenizer import ClipTokenizer

encoder = ClipEncoder(models_dir="./models")
pytestmark = pytest.mark.skipif(
    not encoder.is_installed(), reason="run scripts/fetch_general_model.py first"
)


def test_tokenizer_matches_reference_ids() -> None:
    folder = encoder._folder()
    tokenizer = ClipTokenizer(folder / CLIP_SPEC.vocab_file, folder / CLIP_SPEC.merges_file)
    assert tokenizer.encode("a photo of a cat") == [49406, 320, 1125, 539, 320, 2368, 49407]


def test_zero_shot_probabilities_are_a_distribution() -> None:
    image = np.random.default_rng(0).integers(0, 255, (256, 256, 3), dtype=np.uint8)
    ranked = encoder.group_probabilities(image, CROP_ID_PROMPTS)
    assert {name for name, _ in ranked} == set(CROP_ID_PROMPTS)
    assert sum(p for _, p in ranked) == pytest.approx(1.0, abs=1e-4)
    assert ranked == sorted(ranked, key=lambda item: -item[1])
