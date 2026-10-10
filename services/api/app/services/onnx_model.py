"""ONNX Runtime image classifier wrapper (lazy import, softmax output)."""

import json
from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings
from app.core.model_catalog import ModelSpec


class ModelRuntimeError(RuntimeError):
    """Raised when a model cannot be loaded or executed."""


def weights_path(spec: ModelSpec, models_dir: str | None = None) -> Path:
    """Location where the spec's ONNX file is expected."""
    return Path(models_dir or settings.AI_MODEL_PATH) / spec.weights_file


def _meta_path(weights: Path) -> Path:
    return weights.with_suffix(".meta.json")


def installed_version(spec: ModelSpec, models_dir: str | None = None) -> str:
    """Version from the training sidecar file, else the catalog default."""
    meta = _meta_path(weights_path(spec, models_dir))
    try:
        return str(json.loads(meta.read_text(encoding="utf-8")).get("version", spec.version))
    except (OSError, ValueError):
        return spec.version


def _check_meta_classes(spec: ModelSpec, weights: Path) -> None:
    meta = _meta_path(weights)
    if not meta.exists():
        return
    classes = json.loads(meta.read_text(encoding="utf-8")).get("classes")
    if classes is not None and tuple(classes) != spec.classes:
        raise ModelRuntimeError(f"Class list of '{weights.name}' does not match the catalog.")


class OnnxImageClassifier:
    """Runs one ONNX classifier and returns class probabilities."""

    def __init__(self, spec: ModelSpec, models_dir: str | None = None) -> None:
        self.spec = spec
        weights = weights_path(spec, models_dir)
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise ModelRuntimeError("onnxruntime is not installed.") from exc
        _check_meta_classes(spec, weights)
        try:
            self._session = ort.InferenceSession(str(weights), providers=["CPUExecutionProvider"])
        except Exception as exc:
            raise ModelRuntimeError(f"Could not load '{weights.name}': {exc}") from exc
        out_dim = self._session.get_outputs()[0].shape[-1]
        if isinstance(out_dim, int) and out_dim != len(spec.classes):
            raise ModelRuntimeError(f"'{weights.name}' outputs {out_dim} classes, expected {len(spec.classes)}.")
        self._input_name = self._session.get_inputs()[0].name

    def _preprocess(self, bgr: np.ndarray) -> np.ndarray:
        size = self.spec.input_size
        rgb = cv2.cvtColor(cv2.resize(bgr, (size, size), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        arr = rgb.astype(np.float32) / 255.0
        arr = (arr - np.array(self.spec.mean, np.float32)) / np.array(self.spec.std, np.float32)
        return arr.transpose(2, 0, 1)[None, ...]

    def predict(self, bgr: np.ndarray) -> np.ndarray:
        """Return softmax probabilities in the order of `spec.classes`."""
        logits = self._session.run(None, {self._input_name: self._preprocess(bgr)})[0][0]
        exp = np.exp(logits - np.max(logits))
        return exp / exp.sum()
