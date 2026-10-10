"""Crop identification: a trained classifier when installed, else labelled zero-shot CLIP."""

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from app.core.general_catalog import CLIP_ID_METHOD, CROP_ID_PROMPTS, TRAINED_ID_METHOD
from app.core.model_catalog import CROP_ID_SPEC, ModelSpec
from app.services.clip_runtime import ClipEncoder, clip_encoder
from app.services.onnx_model import ModelRuntimeError, OnnxImageClassifier, weights_path


@dataclass(frozen=True)
class CropIdentification:
    """Ranked crop probabilities, or the reason identification was impossible."""

    available: bool
    candidates: list[tuple[str, float]] = field(default_factory=list)
    reason: str = ""
    method: str = TRAINED_ID_METHOD


class CropIdentifier:
    """Ranks crops (including `unknown`) with the trained model, or zero-shot CLIP if none is installed."""

    def __init__(
        self,
        spec: ModelSpec = CROP_ID_SPEC,
        model_factory: Callable[..., OnnxImageClassifier] = OnnxImageClassifier,
        models_dir: str | None = None,
        zero_shot: ClipEncoder = clip_encoder,
    ) -> None:
        self._zero_shot = zero_shot
        self._spec = spec
        self._factory = model_factory
        self._models_dir = models_dir
        self._model: OnnxImageClassifier | None = None

    def is_installed(self) -> bool:
        return weights_path(self._spec, self._models_dir).exists()

    def identify(self, bgr: np.ndarray) -> CropIdentification:
        if not self.is_installed():
            return self._identify_zero_shot(bgr)
        try:
            if self._model is None:
                self._model = self._factory(self._spec, self._models_dir)
            probs = self._model.predict(bgr)
        except ModelRuntimeError as exc:
            return CropIdentification(False, reason=str(exc))
        ranked = sorted(zip(self._spec.classes, map(float, probs), strict=True), key=lambda x: -x[1])
        return CropIdentification(True, ranked)

    def _identify_zero_shot(self, bgr: np.ndarray) -> CropIdentification:
        """Fallback until crop-ID weights are trained; result is labelled `zero_shot_clip`."""
        reason = "Crop identification weights are not installed."
        if not self._zero_shot.is_installed():
            return CropIdentification(False, reason=reason)
        try:
            ranked = self._zero_shot.group_probabilities(bgr, CROP_ID_PROMPTS)
        except ModelRuntimeError as exc:
            return CropIdentification(False, reason=str(exc))
        return CropIdentification(True, ranked, method=CLIP_ID_METHOD)


crop_identifier = CropIdentifier()
