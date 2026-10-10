"""Registry mapping each crop to its own disease model (never another crop's)."""

from collections.abc import Callable

import numpy as np

from app.core.model_catalog import DISEASE_MODEL_SPECS, ModelSpec
from app.schemas.diagnosis import ModelAvailability
from app.services.onnx_model import (
    ModelRuntimeError,
    OnnxImageClassifier,
    installed_version,
    weights_path,
)


class DiseaseModelRegistry:
    """Looks up, lazily loads and caches per-crop disease classifiers."""

    def __init__(
        self,
        specs: dict[str, ModelSpec] | None = None,
        model_factory: Callable[..., OnnxImageClassifier] = OnnxImageClassifier,
        models_dir: str | None = None,
    ) -> None:
        self._specs = specs if specs is not None else DISEASE_MODEL_SPECS
        self._factory = model_factory
        self._models_dir = models_dir
        self._cache: dict[str, OnnxImageClassifier] = {}

    def has_crop(self, crop: str) -> bool:
        return crop in self._specs

    def availability(self, crop: str) -> str:
        """`available` if this crop's weights exist, else `weights_missing`."""
        spec = self._specs.get(crop)
        if spec is None or not weights_path(spec, self._models_dir).exists():
            return "weights_missing"
        return "available"

    def version(self, crop: str) -> str:
        return installed_version(self._specs[crop], self._models_dir)

    def report(self) -> list[ModelAvailability]:
        return [
            ModelAvailability(
                model=crop,
                status=self.availability(crop),
                weights_file=spec.weights_file,
                version=self.version(crop),
                classes=list(spec.classes),
            )
            for crop, spec in self._specs.items()
        ]

    def predict(self, crop: str, bgr: np.ndarray) -> list[tuple[str, float]]:
        """Return (class, probability) pairs, best first, from `crop`'s own model."""
        spec = self._specs[crop]
        if crop not in self._cache:
            self._cache[crop] = self._factory(spec, self._models_dir)
        probs = self._cache[crop].predict(bgr)
        if len(probs) != len(spec.classes):
            raise ModelRuntimeError(f"Model for '{crop}' returned an unexpected number of classes.")
        return sorted(zip(spec.classes, map(float, probs), strict=True), key=lambda x: -x[1])


disease_model_registry = DiseaseModelRegistry()
