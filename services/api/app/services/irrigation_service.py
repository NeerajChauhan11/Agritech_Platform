"""Service for precision irrigation recommendations and actions."""

from datetime import datetime, timezone

from app.core.config import settings
from app.core.constants import (
    CROP_PROFILES,
    SOIL_MOISTURE_CRITICAL_THRESHOLD,
    TEMP_EXTREME_HEAT_THRESHOLD,
)
from app.core.crops import require_supported_crop
from app.demo import fixtures
from app.schemas.irrigation import (
    IrrigationConfirmRequest,
    IrrigationConfirmResponse,
    IrrigationRecommendation,
    SensorSnapshot,
)


class IrrigationService:
    """Agronomic advisor for precision water management."""

    @classmethod
    def evaluate_irrigation(
        cls,
        field_id: str,
        field_name: str,
        crop: str,
        moisture: float,
        temperature: float,
        humidity: float,
    ) -> IrrigationRecommendation:
        """Calculate water stress level and irrigation recommendation."""
        profile = CROP_PROFILES[require_supported_crop(crop)]
        min_moisture = profile["moisture_min"]
        deficit = min_moisture - moisture
        reasons: list[str] = []

        if moisture <= SOIL_MOISTURE_CRITICAL_THRESHOLD:
            stress, req, duration, conf = "critical", True, 25, 0.96
            reasons.append(f"CRITICAL: Soil moisture ({moisture:.1f}%) is dangerously depleted.")
        elif deficit > 0:
            stress = "high" if deficit >= 8.0 else "medium"
            req = True
            duration = min(30, max(5, int(deficit * 2.0)))
            conf = 0.88 if stress == "high" else 0.76
            reasons.append(f"Soil moisture ({moisture:.1f}%) is below optimal minimum ({min_moisture:.1f}%).")
        else:
            stress, req, duration, conf = "low", False, 0, 0.92
            reasons.append(f"Soil moisture ({moisture:.1f}%) is adequate for {crop}.")

        if temperature >= TEMP_EXTREME_HEAT_THRESHOLD:
            reasons.append(f"High ambient temperature ({temperature:.1f}°C) accelerates evapotranspiration.")

        return IrrigationRecommendation(
            field_id=field_id,
            field_name=field_name,
            crop=crop,
            water_stress=stress,
            irrigation_required=req,
            estimated_duration_minutes=duration,
            confidence=conf,
            reasons=reasons,
            sensor_snapshot=SensorSnapshot(
                soil_moisture=moisture,
                temperature=temperature,
                humidity=humidity,
            ),
        )

    @classmethod
    async def get_recommendations(cls) -> list[IrrigationRecommendation]:
        """Fetch current water stress and irrigation recommendations."""
        if settings.DEMO_MODE:
            return fixtures.DEMO_IRRIGATION
        return fixtures.DEMO_IRRIGATION

    @classmethod
    async def confirm_irrigation(
        cls,
        request: IrrigationConfirmRequest,
    ) -> IrrigationConfirmResponse:
        """Confirm farmer acknowledgment and dispatch valve trigger."""
        duration = request.duration_minutes or 15
        now_iso = datetime.now(timezone.utc).isoformat()
        return IrrigationConfirmResponse(
            field_id=request.field_id,
            status="scheduled",
            message=f"Irrigation scheduled for {duration} minutes on {request.field_id}.",
            confirmed_at=now_iso,
        )


irrigation_service = IrrigationService()
