"""Schemas for automatic crop identification and disease diagnosis."""

from typing import Literal

from pydantic import BaseModel, Field

DiagnosisStatus = Literal[
    "ok",
    "low_quality_image",
    "crop_uncertain",
    "crop_unsupported",
    "model_unavailable",
    "disease_uncertain",
]
Severity = Literal["low", "moderate", "high", "none"]
DiagnosisTier = Literal["specific", "general_category"]
CropIdMethod = Literal["trained_classifier", "zero_shot_clip"]


class PredictionItem(BaseModel):
    """Ranked candidate (crop or disease) with its probability."""

    label: str
    display_name: str
    probability: float = Field(..., ge=0.0, le=1.0)


class Recommendations(BaseModel):
    """Actionable guidance for a diagnosed condition."""

    treatment: list[str]
    prevention: list[str]


class CategoryResult(BaseModel):
    """Coarse condition category from the general (zero-shot) tier; never a specific disease."""

    id: str
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class CategoryGuidance(BaseModel):
    """Plain-language advice for a general category on the identified crop."""

    description: str
    look_for: list[str]
    consult: str


class XaiResult(BaseModel):
    """Explainable AI metadata (only set when a real attention map exists)."""

    method: str
    heatmap_url: str


class DiagnosisResult(BaseModel):
    """Complete diagnostic payload for one uploaded leaf image."""

    status: DiagnosisStatus
    message: str
    user_action: str = ""
    detected_crop: str | None = None
    crop_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    crop_candidates: list[PredictionItem] = Field(default_factory=list)
    disease_label: str | None = None
    disease_name: str | None = None
    disease_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    severity: Severity | None = None
    predictions: list[PredictionItem] = Field(default_factory=list)
    symptoms: list[str] = Field(default_factory=list)
    recommendations: Recommendations | None = None
    model_version: str | None = None
    diagnosis_tier: DiagnosisTier | None = None  # None when no disease analysis ran
    tier_notice: str | None = None  # shown verbatim in the UI for general-tier results
    crop_id_method: CropIdMethod | None = None
    category: CategoryResult | None = None
    category_predictions: list[PredictionItem] = Field(default_factory=list)
    category_guidance: CategoryGuidance | None = None
    xai: XaiResult | None = None


class ModelAvailability(BaseModel):
    """Whether the weights for one model are installed."""

    model: str
    status: Literal["available", "weights_missing"]
    weights_file: str
    version: str
    classes: list[str]
