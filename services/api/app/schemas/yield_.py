"""Schemas for yield prediction and contributing agro-climatic factors."""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionInterval(BaseModel):
    """Lower and upper bounds for yield interval estimation."""

    lower: float
    upper: float


class YieldFactor(BaseModel):
    """Factor influencing harvest yields."""

    name: str
    impact: Literal["positive", "negative", "neutral"]
    weight: float = Field(..., ge=0.0, le=1.0)


class YieldPrediction(BaseModel):
    """Crop harvest yield forecast."""

    crop: str
    field_id: str
    field_name: str
    estimated_yield_t_per_hectare: float = Field(..., ge=0.0)
    prediction_interval: PredictionInterval
    confidence: float = Field(..., ge=0.0, le=1.0)
    factors: list[YieldFactor]
    last_season_yield: float = Field(..., ge=0.0)


class YieldPredictRequest(BaseModel):
    """Request payload to calculate or retrieve yield forecast."""

    field_id: str
    crop: str | None = None
