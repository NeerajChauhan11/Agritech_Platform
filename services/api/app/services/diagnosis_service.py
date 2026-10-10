"""Orchestrates automatic diagnosis: quality gate -> crop ID -> crop model -> result."""

import io

import numpy as np
from PIL import Image

from app.core.constants import (
    CROP_CONFIDENCE_MIN,
    CROP_MARGIN_MIN,
    CROP_UNKNOWN_CLASS,
    DIAGNOSIS_STATUS_MESSAGES,
    DIAGNOSIS_TOP_K,
    DISEASE_CONFIDENCE_MIN,
    QUALITY_ISSUE_MESSAGES,
)
from app.core.crops import crop_display_name
from app.core.general_catalog import CLIP_SPEC, GENERAL_CATEGORIES, TIER_SPECIFIC
from app.knowledge.disease_info import get_disease_info
from app.schemas.diagnosis import (
    DiagnosisResult,
    ModelAvailability,
    PredictionItem,
    Recommendations,
)
from app.services.crop_identifier import CropIdentification, crop_identifier
from app.services.disease_model_registry import disease_model_registry
from app.services.general_category_classifier import general_classifier
from app.services.general_diagnosis import general_outcome
from app.services.image_quality import decode_image, image_quality_gate
from app.services.onnx_model import ModelRuntimeError

NOT_A_LEAF_NAME = "Not a recognised crop leaf"


def _crop_items(candidates: list[tuple[str, float]]) -> list[PredictionItem]:
    return [
        PredictionItem(
            label=label,
            display_name=NOT_A_LEAF_NAME if label == CROP_UNKNOWN_CLASS else crop_display_name(label),
            probability=round(prob, 4),
        )
        for label, prob in candidates[:DIAGNOSIS_TOP_K]
    ]


class DiagnosisService:
    """Automatic crop identification followed by crop-specific disease analysis."""

    def __init__(self) -> None:
        self.identifier = crop_identifier
        self.registry = disease_model_registry
        self.general = general_classifier
        self.quality_gate = image_quality_gate

    def model_report(self) -> list[ModelAvailability]:
        """Per-crop specific models, then the shared general-category tier."""
        installed = self.general.is_installed()
        general = ModelAvailability(
            model="general_category",
            status="available" if installed else "weights_missing",
            weights_file=f"{CLIP_SPEC.folder}/{CLIP_SPEC.vision_file}",
            version=self.general.version() if installed else "not installed",
            classes=list(GENERAL_CATEGORIES),
        )
        return [*self.registry.report(), general]

    @staticmethod
    def validate_image_payload(image_bytes: bytes) -> None:
        """Raise ValueError unless the payload is a readable image."""
        if not image_bytes or len(image_bytes) < 32:
            raise ValueError("Uploaded file is empty or corrupted.")
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
        except Exception as exc:
            raise ValueError("Uploaded file is not a valid image format.") from exc

    @staticmethod
    def _result(status: str, message: str | None = None, **fields: object) -> DiagnosisResult:
        default_message, user_action = DIAGNOSIS_STATUS_MESSAGES[status]
        return DiagnosisResult(
            status=status, message=message or default_message, user_action=user_action, **fields
        )

    def _evaluate_crop(self, candidates: list[tuple[str, float]]) -> tuple[str | None, str | None]:
        """Return (crop_key, None) if accepted, else (None, failure_status)."""
        (top_label, top_p), second_p = candidates[0], candidates[1][1]
        if (
            top_label == CROP_UNKNOWN_CLASS
            or top_p < CROP_CONFIDENCE_MIN
            or top_p - second_p < CROP_MARGIN_MIN
        ):
            return None, "crop_uncertain"
        if not self.registry.has_crop(top_label):
            return None, "crop_unsupported"
        return top_label, None

    def _identify(self, image: np.ndarray) -> tuple[CropIdentification, str | None, str | None]:
        ident = self.identifier.identify(image)
        if not ident.available:
            return ident, None, "model_unavailable"
        crop, failure = self._evaluate_crop(ident.candidates)
        return ident, crop, failure

    @staticmethod
    def _disease_name(crop: str, label: str) -> str:
        found = get_disease_info(crop, label)
        return found.display_name if found else label.replace("_", " ").title()

    def _diagnose_disease(
        self, image: np.ndarray, crop: str, ident: CropIdentification
    ) -> DiagnosisResult:
        """Specific per-crop model if installed and runnable, else the general-category tier."""
        crop_fields = {
            "detected_crop": crop_display_name(crop),
            "crop_confidence": round(ident.candidates[0][1], 4),
            "crop_candidates": _crop_items(ident.candidates),
            "crop_id_method": ident.method,
        }
        if self.registry.availability(crop) == "available":
            specific = self._diagnose_specific(image, crop, crop_fields)
            if specific is not None:
                return specific
        outcome = general_outcome(self.general, image, crop, crop_fields)
        if outcome is None:
            msg = f"The {crop_display_name(crop)} disease model is not installed on the server."
            return self._result("model_unavailable", msg, **crop_fields)
        status, message, fields = outcome
        return self._result(status, message, **fields)

    def _diagnose_specific(self, image: np.ndarray, crop: str, crop_fields: dict) -> DiagnosisResult | None:
        """Run the crop's own model; None if it cannot be run."""
        try:
            ranked = self.registry.predict(crop, image)
        except ModelRuntimeError:
            return None
        predictions = [
            PredictionItem(
                label=label, display_name=self._disease_name(crop, label), probability=round(p, 4)
            )
            for label, p in ranked[:DIAGNOSIS_TOP_K]
        ]
        fields = {
            **crop_fields,
            "predictions": predictions,
            "model_version": self.registry.version(crop),
            "diagnosis_tier": TIER_SPECIFIC,
        }
        top_label, top_p = ranked[0]
        if top_p < DISEASE_CONFIDENCE_MIN:
            return self._result("disease_uncertain", disease_confidence=round(top_p, 4), **fields)
        return self._confident_result(crop, top_label, top_p, fields)

    def _confident_result(self, crop: str, label: str, prob: float, fields: dict) -> DiagnosisResult:
        found = get_disease_info(crop, label)
        name = self._disease_name(crop, label)
        message = "No disease detected." if label == "healthy" else f"{name} detected on {crop_display_name(crop)}."
        guidance = (
            Recommendations(treatment=list(found.treatment), prevention=list(found.prevention))
            if found
            else None
        )
        return self._result(
            "ok",
            message,
            disease_label=label,
            disease_name=name,
            disease_confidence=round(prob, 4),
            severity=found.severity if found else None,
            symptoms=list(found.symptoms) if found else [],
            recommendations=guidance,
            **fields,
        )

    async def diagnose_leaf_image(self, image_bytes: bytes) -> DiagnosisResult:
        """Run the full pipeline; never invents a disease when a stage fails."""
        self.validate_image_payload(image_bytes)
        image = decode_image(image_bytes)

        report = self.quality_gate.assess(image)
        if not report.ok:
            message, action = QUALITY_ISSUE_MESSAGES[report.issue or "unreadable"]
            result = self._result("low_quality_image", message)
            return result.model_copy(update={"user_action": action})

        ident, crop, failure = self._identify(image)
        if failure == "model_unavailable":
            return self._result(failure, ident.reason)
        if crop is None:
            return self._result(
                failure or "crop_uncertain",
                crop_candidates=_crop_items(ident.candidates),
                crop_confidence=round(ident.candidates[0][1], 4),
                crop_id_method=ident.method,
            )
        return self._diagnose_disease(image, crop, ident)


diagnosis_service = DiagnosisService()
