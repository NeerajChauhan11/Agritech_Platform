"""Catalog for the general-category (zero-shot CLIP) tier: files, categories and text prompts.

Prompts are the only "labels" the zero-shot model sees, so wording changes alter results.
`{crop}` is replaced with the identified crop's display name.
"""

from dataclasses import dataclass
from typing import Final

from app.core.constants import CROP_UNKNOWN_CLASS, SUPPORTED_CROPS


@dataclass(frozen=True)
class ClipSpec:
    """Where the CLIP ONNX files live (inside the models folder) and how to feed them."""

    folder: str = "clip_general"
    vision_file: str = "vision_model.onnx"
    text_file: str = "text_model.onnx"
    vocab_file: str = "vocab.json"
    merges_file: str = "merges.txt"
    meta_file: str = "meta.json"
    input_size: int = 224
    mean: tuple[float, float, float] = (0.48145466, 0.4578275, 0.40821073)
    std: tuple[float, float, float] = (0.26862954, 0.26130258, 0.27577711)
    logit_scale: float = 100.0  # CLIP's trained temperature (exp of the learned logit scale)


CLIP_SPEC: Final[ClipSpec] = ClipSpec()
CLIP_ID_METHOD: Final[str] = "zero_shot_clip"
TRAINED_ID_METHOD: Final[str] = "trained_classifier"

TIER_GENERAL: Final[str] = "general_category"
TIER_SPECIFIC: Final[str] = "specific"
GENERAL_TIER_NOTICE: Final[str] = (
    "Preliminary category screening — specific-disease model is in training"
)

# id -> label. One shared list for backend, knowledge module and frontend types.
GENERAL_CATEGORIES: Final[dict[str, str]] = {
    "healthy": "Healthy",
    "fungal": "Fungal leaf disease",
    "bacterial": "Bacterial disease",
    "viral": "Viral disease",
    "pest": "Pest damage",
    "nutrient_stress": "Nutrient deficiency / stress",
}
# Categories offered per crop (all six are agronomically relevant to all three crops).
CROP_CATEGORIES: Final[dict[str, tuple[str, ...]]] = {
    crop: tuple(GENERAL_CATEGORIES) for crop in SUPPORTED_CROPS
}

CATEGORY_PROMPTS: Final[dict[str, tuple[str, ...]]] = {
    "healthy": (
        "a photo of a healthy green {crop} leaf",
        "a close-up of a {crop} leaf with no spots or damage",
    ),
    "fungal": (
        "a photo of a {crop} leaf with brown fungal spots",
        "a {crop} leaf with blight, rust or mildew lesions",
    ),
    "bacterial": (
        "a photo of a {crop} leaf with small dark water-soaked bacterial spots",
        "a {crop} leaf with angular black bacterial lesions",
    ),
    "viral": (
        "a photo of a {crop} leaf with mosaic pattern and curling from a virus",
        "a yellow, mottled and twisted {crop} leaf",
    ),
    "pest": (
        "a photo of a {crop} leaf eaten by insects with holes",
        "a {crop} leaf damaged by mites or insects",
    ),
    "nutrient_stress": (
        "a photo of a {crop} leaf with yellowing from nutrient deficiency",
        "a {crop} leaf with scorched dry edges",
    ),
}

# Crop identification prompts. Every non-supported concept maps to `unknown`.
_UNKNOWN_SUBJECTS: Final[tuple[str, ...]] = (
    "a photo of a wheat plant leaf",
    "a photo of a sugarcane leaf",
    "a photo of a rice plant leaf",
    "a photo of a corn leaf",
    "a photo of a potato leaf",
    "a photo of a grape leaf",
    "a photo of a cucumber leaf",
    "a photo of grass",
    "a photo of a tree with leaves of another species",
    "a photo of a flower",
    "a photo of a person",
    "a photo of an animal",
    "a photo of a building",
    "a photo of a room or an object",
    "a photo of a document or text",
    "a photo of soil",
    "a photo of a fruit",
)
CROP_ID_PROMPTS: Final[dict[str, tuple[str, ...]]] = {
    "apple": (
        "a photo of an apple leaf",
        "a single oval serrated apple tree leaf",
        "a leaf from an apple tree",
    ),
    "tomato": (
        "a photo of a tomato leaf",
        "a tomato plant leaf with lobed jagged leaflets",
        "a leaf from a tomato plant",
    ),
    "capsicum": (
        "a photo of a pepper leaf",
        "a smooth glossy pointed pepper plant leaf",
        "a leaf from a bell pepper or capsicum plant",
    ),
    CROP_UNKNOWN_CLASS: _UNKNOWN_SUBJECTS,
}

# Names used inside prompts (CLIP knows "bell pepper" better than "capsicum").
CROP_PROMPT_NAMES: Final[dict[str, str]] = {"apple": "apple", "tomato": "tomato", "capsicum": "bell pepper"}
