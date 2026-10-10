"""Crop identifier normalisation and validation against the supported-crop list."""

from app.core.constants import (
    CROP_ALIASES,
    CROP_DISPLAY_NAMES,
    CROP_NOT_SUPPORTED_CODE,
    SUPPORTED_CROPS,
)


class UnsupportedCropError(ValueError):
    """Raised when a caller supplies a crop outside SUPPORTED_CROPS."""

    code = CROP_NOT_SUPPORTED_CODE


def supported_crops_text() -> str:
    """'apple, tomato, capsicum' in canonical order."""
    return ", ".join(SUPPORTED_CROPS)


def normalize_crop(value: str | None) -> str | None:
    """Return the canonical crop id for `value`, or None if it is not supported."""
    if value is None:
        return None
    key = "_".join(value.strip().lower().replace("-", " ").split())
    key = CROP_ALIASES.get(key, key)
    return key if key in SUPPORTED_CROPS else None


def require_supported_crop(value: str) -> str:
    """Canonical crop id, or UnsupportedCropError. Never falls back to another crop."""
    crop = normalize_crop(value)
    if crop is None:
        raise UnsupportedCropError(
            f"Crop '{value}' is not supported. Supported crops: {supported_crops_text()}."
        )
    return crop


def crop_display_name(crop: str) -> str:
    return CROP_DISPLAY_NAMES.get(crop, crop.replace("_", " ").title())
