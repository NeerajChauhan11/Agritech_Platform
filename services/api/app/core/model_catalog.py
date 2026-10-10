"""Catalog of expected models: crops, class lists, input sizes and weight files.

Class order here is the output order the ONNX model must be trained with
(scripts/train_disease_model.py reads this file, so the two cannot drift).
"""

from dataclasses import dataclass

from app.core.constants import CROP_UNKNOWN_CLASS, SUPPORTED_CROPS

IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)
DEFAULT_ARCHITECTURE = "mobilenet_v3_large"
UNRELEASED_VERSION = "unreleased"


@dataclass(frozen=True)
class ModelSpec:
    """Everything needed to locate, validate and run one ONNX classifier."""

    key: str
    weights_file: str
    classes: tuple[str, ...]
    input_size: int = 224
    mean: tuple[float, float, float] = IMAGENET_MEAN
    std: tuple[float, float, float] = IMAGENET_STD
    architecture: str = DEFAULT_ARCHITECTURE
    version: str = UNRELEASED_VERSION


def _spec(crop: str, classes: tuple[str, ...]) -> ModelSpec:
    return ModelSpec(key=crop, weights_file=f"disease_{crop}.onnx", classes=classes)


CROP_ID_SPEC = ModelSpec(
    key="crop_id",
    weights_file="crop_id.onnx",
    classes=(*sorted(SUPPORTED_CROPS), CROP_UNKNOWN_CLASS),
)

# Class lists follow public datasets; see docs/models.md for sources.
# Keys must match SUPPORTED_CROPS exactly (asserted below and in the tests).
DISEASE_MODEL_SPECS: dict[str, ModelSpec] = {
    "apple": _spec("apple", ("apple_scab", "black_rot", "cedar_apple_rust", "healthy")),
    "tomato": _spec("tomato", (
        "bacterial_spot", "early_blight", "late_blight", "leaf_mold", "septoria_leaf_spot",
        "spider_mites", "target_spot", "yellow_leaf_curl_virus", "mosaic_virus", "healthy",
    )),
    "capsicum": _spec("capsicum", ("bacterial_spot", "healthy")),
}
assert tuple(DISEASE_MODEL_SPECS) == SUPPORTED_CROPS, "model catalog out of sync with SUPPORTED_CROPS"
