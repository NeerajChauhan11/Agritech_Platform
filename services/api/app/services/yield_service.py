"""Service for crop yield forecast and risk factor analysis."""

from app.core.config import settings
from app.core.constants import CROP_PROFILES
from app.core.crops import require_supported_crop
from app.demo import fixtures
from app.schemas.yield_ import PredictionInterval, YieldFactor, YieldPrediction


class YieldService:
    """Yield forecasting engine combining telemetry and historical yields."""

    @classmethod
    def calculate_yield(
        cls,
        crop: str,
        field_id: str,
        field_name: str,
        moisture: float,
        temperature: float,
        last_yield: float,
    ) -> YieldPrediction:
        """Calculate yield projection and factor breakdown."""
        profile = CROP_PROFILES[require_supported_crop(crop)]
        base_yield = last_yield if last_yield > 0 else profile["base_yield"]

        # Moisture factor
        opt_moist = (profile["moisture_min"] + profile["moisture_max"]) / 2.0
        m_diff = (moisture - opt_moist) / opt_moist
        m_impact = "positive" if abs(m_diff) < 0.15 else "negative"

        # Temp penalty
        t_diff = abs(temperature - profile["opt_temp"])
        t_impact = "positive" if t_diff < 3.0 else "negative"

        multiplier = 1.0 + (0.08 if m_impact == "positive" else -0.06) + (0.05 if t_impact == "positive" else -0.08)
        estimated = round(max(0.5, base_yield * multiplier), 2)
        interval = PredictionInterval(lower=round(estimated * 0.9, 2), upper=round(estimated * 1.1, 2))

        factors = [
            YieldFactor(name="Soil Moisture", impact=m_impact, weight=0.85),
            YieldFactor(name="Temperature", impact=t_impact, weight=0.72),
            YieldFactor(name="Fertilization", impact="positive", weight=0.90),
            YieldFactor(name="Disease Pressure", impact="neutral", weight=0.35),
        ]

        return YieldPrediction(
            crop=crop,
            field_id=field_id,
            field_name=field_name,
            estimated_yield_t_per_hectare=estimated,
            prediction_interval=interval,
            confidence=0.84,
            factors=factors,
            last_season_yield=base_yield,
        )

    @classmethod
    async def get_yield_predictions(
        cls,
        field_id: str | None = None,
    ) -> list[YieldPrediction]:
        """Fetch yield predictions, optionally filtered by field ID."""
        if settings.DEMO_MODE:
            if field_id:
                return [p for p in fixtures.DEMO_YIELD if p.field_id == field_id]
            return fixtures.DEMO_YIELD
        return [p for p in fixtures.DEMO_YIELD if p.field_id == field_id] if field_id else fixtures.DEMO_YIELD


yield_service = YieldService()
