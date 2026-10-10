"""Builds the general-category (preliminary screening) outcome for an identified crop."""

import numpy as np

from app.core.constants import (
    CATEGORY_CONFIDENCE_MIN,
    CATEGORY_MARGIN_MIN,
    DIAGNOSIS_TOP_K,
)
from app.core.crops import crop_display_name
from app.core.general_catalog import (
    GENERAL_CATEGORIES,
    GENERAL_TIER_NOTICE,
    TIER_GENERAL,
)
from app.knowledge.general_categories import get_category_guidance
from app.schemas.diagnosis import (
    CategoryGuidance,
    CategoryResult,
    PredictionItem,
    Recommendations,
)
from app.services.general_category_classifier import GeneralCategoryClassifier
from app.services.onnx_model import ModelRuntimeError

UNCERTAIN_MESSAGE = "The preliminary screen is not confident enough to name a condition category."
Outcome = tuple[str, str | None, dict]  # (status, message override, result fields)


def _items(ranked: list[tuple[str, float]]) -> list[PredictionItem]:
    return [
        PredictionItem(label=cid, display_name=GENERAL_CATEGORIES[cid], probability=round(p, 4))
        for cid, p in ranked[:DIAGNOSIS_TOP_K]
    ]


def _accepted(ranked: list[tuple[str, float]]) -> bool:
    (_, top), second = ranked[0], ranked[1][1]
    return top >= CATEGORY_CONFIDENCE_MIN and top - second >= CATEGORY_MARGIN_MIN


def _ok_fields(crop: str, ranked: list[tuple[str, float]]) -> tuple[str, dict]:
    category, prob = ranked[0]
    label = GENERAL_CATEGORIES[category]
    guidance = get_category_guidance(crop, category)
    fields: dict = {"category": CategoryResult(id=category, label=label, confidence=round(prob, 4))}
    if guidance:
        fields.update(
            symptoms=list(guidance.look_for),
            recommendations=Recommendations(treatment=list(guidance.actions), prevention=list(guidance.prevention)),
            category_guidance=CategoryGuidance(
                description=guidance.description, look_for=list(guidance.look_for), consult=guidance.consult
            ),
        )
    crop_name = crop_display_name(crop)
    if category == "healthy":
        return f"Preliminary screening: no clear disease signs on this {crop_name} leaf.", fields
    return f"Preliminary screening: the leaf pattern is most consistent with {label.lower()} on {crop_name}.", fields


def general_outcome(
    classifier: GeneralCategoryClassifier, image: np.ndarray, crop: str, crop_fields: dict
) -> Outcome | None:
    """Run the general tier; None if it cannot run (weights missing or not loadable)."""
    if not classifier.is_installed():
        return None
    try:
        ranked = classifier.classify(image, crop)
    except ModelRuntimeError:
        return None
    fields = {
        **crop_fields,
        "diagnosis_tier": TIER_GENERAL,
        "tier_notice": GENERAL_TIER_NOTICE,
        "category_predictions": _items(ranked),
        "model_version": classifier.version(),
    }
    if not _accepted(ranked):
        return "disease_uncertain", UNCERTAIN_MESSAGE, fields
    message, ok_fields = _ok_fields(crop, ranked)
    return "ok", message, {**fields, **ok_fields}
