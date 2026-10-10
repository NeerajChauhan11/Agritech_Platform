"""Image-quality gate: rejects unusable photos before any model runs."""

from dataclasses import dataclass

import cv2
import numpy as np

from app.core.constants import (
    QUALITY_BLUR_LAPLACIAN_MIN,
    QUALITY_BRIGHTNESS_MAX,
    QUALITY_BRIGHTNESS_MIN,
    QUALITY_CLIPPED_MAX_FRACTION,
    QUALITY_LEAF_COVERAGE_MIN,
    QUALITY_MIN_SIDE_PX,
)

_ANALYSIS_MAX_SIDE = 512
# OpenCV hue range covering brown/yellow/green plant tissue.
_LEAF_HUE_RANGE = (8, 95)
_LEAF_MIN_SATURATION = 40
_LEAF_MIN_VALUE = 40


@dataclass(frozen=True)
class QualityReport:
    """Outcome of the quality gate; `issue` is a QUALITY_ISSUE_MESSAGES key."""

    ok: bool
    issue: str | None = None


def decode_image(image_bytes: bytes) -> np.ndarray | None:
    """Decode bytes to a BGR array, or None if undecodable."""
    return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)


def _shrink(image: np.ndarray) -> np.ndarray:
    scale = _ANALYSIS_MAX_SIDE / max(image.shape[:2])
    if scale >= 1.0:
        return image
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def _exposure_issue(gray: np.ndarray) -> str | None:
    mean = float(gray.mean())
    clipped = float(np.mean((gray < 8) | (gray > 247)))
    if mean < QUALITY_BRIGHTNESS_MIN or (clipped > QUALITY_CLIPPED_MAX_FRACTION and mean < 128):
        return "too_dark"
    if mean > QUALITY_BRIGHTNESS_MAX or (clipped > QUALITY_CLIPPED_MAX_FRACTION and mean >= 128):
        return "too_bright"
    return None


def _leaf_coverage(bgr: np.ndarray) -> float:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    mask = (
        (hue >= _LEAF_HUE_RANGE[0]) & (hue <= _LEAF_HUE_RANGE[1])
        & (sat >= _LEAF_MIN_SATURATION) & (val >= _LEAF_MIN_VALUE)
    )
    return float(mask.mean())


class ImageQualityGate:
    """Blur, exposure, resolution and leaf-coverage checks (no diagnosis logic)."""

    @staticmethod
    def assess(image: np.ndarray | None) -> QualityReport:
        if image is None:
            return QualityReport(False, "unreadable")
        if min(image.shape[:2]) < QUALITY_MIN_SIDE_PX:
            return QualityReport(False, "low_resolution")

        small = _shrink(image)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        issue = _exposure_issue(gray)
        if issue:
            return QualityReport(False, issue)
        if cv2.Laplacian(gray, cv2.CV_64F).var() < QUALITY_BLUR_LAPLACIAN_MIN:
            return QualityReport(False, "blurry")
        if _leaf_coverage(small) < QUALITY_LEAF_COVERAGE_MIN:
            return QualityReport(False, "no_leaf")
        return QualityReport(True)


image_quality_gate = ImageQualityGate()
