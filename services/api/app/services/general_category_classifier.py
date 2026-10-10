"""General-category tier: zero-shot CLIP scoring of a leaf image against condition categories."""

import numpy as np

from app.core.general_catalog import (
    CATEGORY_PROMPTS,
    CROP_CATEGORIES,
    CROP_PROMPT_NAMES,
)
from app.services.clip_runtime import ClipEncoder, clip_encoder


class GeneralCategoryClassifier:
    """Ranks the categories offered for a crop. Scores are relative and NOT calibrated."""

    def __init__(self, encoder: ClipEncoder = clip_encoder) -> None:
        self._encoder = encoder

    def is_installed(self) -> bool:
        return self._encoder.is_installed()

    def version(self) -> str:
        return self._encoder.version()

    def classify(self, bgr: np.ndarray, crop: str) -> list[tuple[str, float]]:
        """Return (category id, probability) pairs, best first. Raises ModelRuntimeError if unloadable."""
        name = CROP_PROMPT_NAMES[crop]
        groups = {
            category: tuple(template.format(crop=name) for template in CATEGORY_PROMPTS[category])
            for category in CROP_CATEGORIES[crop]
        }
        return self._encoder.group_probabilities(bgr, groups)


general_classifier = GeneralCategoryClassifier()
