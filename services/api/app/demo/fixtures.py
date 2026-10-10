"""Demo fixtures matching frontend lib/demo-data.ts."""

from datetime import datetime, timezone

from app.schemas.alerts import Alert
from app.schemas.diagnosis import (
    DiagnosisResult,
    PredictionItem,
)
from app.schemas.farm import Device, Farm, FieldSchema
from app.schemas.irrigation import IrrigationRecommendation, SensorSnapshot
from app.schemas.telemetry import SensorReading, TelemetryPoint
from app.schemas.yield_ import PredictionInterval, YieldFactor, YieldPrediction

# ── Demo Farm ─────────────────────────────────────────────────────────────────
DEMO_FARM: Farm = Farm(
    id="farm-alpha",
    name="Green Valley Farm",
    location="Chandigarh, Punjab, India",
    total_area_hectares=24.5,
    overall_health=78.0,
    fields=[
        FieldSchema(
            id="field-01",
            name="Tomato Field A",
            farm_id="farm-alpha",
            crop="Tomato",
            area_hectares=5.2,
            health_score=82.0,
            status="healthy",
            growth_stage="Fruiting",
            coordinates=(30.7333, 76.7794),
            devices=[
                Device(id="esp32-node-01", name="Node-01", field_id="field-01", status="online", last_seen="Just now", battery=87, signal=94),
                Device(id="esp32-node-02", name="Node-02", field_id="field-01", status="online", last_seen="1 min ago", battery=72, signal=88),
            ],
            latest_reading=SensorReading(
                timestamp=datetime.now(timezone.utc).isoformat(),
                soil_moisture=42.5,
                temperature=28.4,
                humidity=65.0,
                ph_level=6.8,
                nitrogen=42.0,
                phosphorus=28.0,
                potassium=36.0,
            ),
        ),
        FieldSchema(
            id="field-02",
            name="Apple Orchard B",
            farm_id="farm-alpha",
            crop="Apple",
            area_hectares=8.1,
            health_score=61.0,
            status="warning",
            growth_stage="Fruit Set",
            coordinates=(30.7401, 76.7820),
            devices=[
                Device(id="esp32-node-03", name="Node-03", field_id="field-02", status="warning", last_seen="3 min ago", battery=31, signal=65),
                Device(id="esp32-node-04", name="Node-04", field_id="field-02", status="online", last_seen="Just now", battery=91, signal=97),
            ],
            latest_reading=SensorReading(
                timestamp=datetime.now(timezone.utc).isoformat(),
                soil_moisture=29.1,
                temperature=31.2,
                humidity=52.0,
                ph_level=7.2,
                nitrogen=35.0,
                phosphorus=22.0,
                potassium=28.0,
            ),
        ),
        FieldSchema(
            id="field-03",
            name="Capsicum Field C",
            farm_id="farm-alpha",
            crop="Capsicum",
            area_hectares=6.4,
            health_score=91.0,
            status="healthy",
            growth_stage="Flowering",
            coordinates=(30.7280, 76.7760),
            devices=[
                Device(id="esp32-node-05", name="Node-05", field_id="field-03", status="online", last_seen="Just now", battery=78, signal=92),
            ],
            latest_reading=SensorReading(
                timestamp=datetime.now(timezone.utc).isoformat(),
                soil_moisture=68.3,
                temperature=26.8,
                humidity=74.0,
                ph_level=6.4,
                nitrogen=55.0,
                phosphorus=31.0,
                potassium=42.0,
            ),
        ),
        FieldSchema(
            id="field-04",
            name="Tomato Field D",
            farm_id="farm-alpha",
            crop="Tomato",
            area_hectares=4.8,
            health_score=44.0,
            status="critical",
            growth_stage="Flowering",
            coordinates=(30.7350, 76.7850),
            devices=[
                Device(id="esp32-node-06", name="Node-06", field_id="field-04", status="offline", last_seen="2 hrs ago", battery=12, signal=0),
            ],
            latest_reading=SensorReading(
                timestamp=datetime.now(timezone.utc).isoformat(),
                soil_moisture=18.2,
                temperature=33.5,
                humidity=44.0,
                ph_level=7.8,
                nitrogen=28.0,
                phosphorus=18.0,
                potassium=22.0,
            ),
        ),
    ],
)

# ── Demo Telemetry Points ────────────────────────────────────────────────────
def _generate_telemetry_points(base_moisture: float, base_temp: float, base_hum: float, base_ph: float) -> list[TelemetryPoint]:
    points: list[TelemetryPoint] = []
    for hour in range(24):
        time_str = f"{hour:02d}:00"
        factor = 1.0 + ((hour % 5) - 2) * 0.02
        points.append(
            TelemetryPoint(
                time=time_str,
                moisture=round(base_moisture * factor, 1),
                temperature=round(base_temp * factor, 1),
                humidity=round(base_hum * factor, 1),
                ph=round(base_ph, 2),
            )
        )
    return points

DEMO_TELEMETRY: dict[str, list[TelemetryPoint]] = {
    "field-01": _generate_telemetry_points(42.5, 28.4, 65.0, 6.8),
    "field-02": _generate_telemetry_points(29.1, 31.2, 52.0, 7.2),
    "field-03": _generate_telemetry_points(68.3, 26.8, 74.0, 6.4),
    "field-04": _generate_telemetry_points(18.2, 33.5, 44.0, 7.8),
}

# ── Demo Alerts ──────────────────────────────────────────────────────────────
DEMO_ALERTS: list[Alert] = [
    Alert(
        id="alert-01",
        field_id="field-04",
        field_name="Tomato Field D",
        category="sensor",
        severity="critical",
        title="Sensor Node Offline",
        message="Node-06 has been offline for 2+ hours. Last soil moisture reading was critically low at 18.2%.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        acknowledged=False,
    ),
    Alert(
        id="alert-02",
        field_id="field-04",
        field_name="Tomato Field D",
        category="irrigation",
        severity="critical",
        title="Critical Water Stress",
        message="Soil moisture at 18.2% — well below the 45% minimum for tomato. Immediate irrigation required.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        acknowledged=False,
    ),
    Alert(
        id="alert-03",
        field_id="field-02",
        field_name="Apple Orchard B",
        category="disease",
        severity="warning",
        title="Disease Risk Elevated",
        message="Heat (31.2°C) and low humidity (52%) increase plant stress and susceptibility to fungal disease. Inspect crop.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        acknowledged=False,
    ),
    Alert(
        id="alert-04",
        field_id="field-02",
        field_name="Apple Orchard B",
        category="sensor",
        severity="warning",
        title="Low Battery — Node-03",
        message="Node-03 battery at 31%. Consider recharging to avoid data gaps.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        acknowledged=False,
    ),
    Alert(
        id="alert-05",
        field_id="field-01",
        field_name="Tomato Field A",
        category="irrigation",
        severity="info",
        title="Irrigation Recommended",
        message="Soil moisture trending downward. AI recommends 12-minute irrigation cycle within the next 4 hours.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        acknowledged=True,
    ),
]

# ── Demo Diagnosis ───────────────────────────────────────────────────────────
# Illustrative payload in the real response schema. Never returned by the
# diagnosis route: results always come from trained models (see docs/models.md).
DEMO_DIAGNOSIS: DiagnosisResult = DiagnosisResult(
    status="ok",
    message="Early Blight (Alternaria solani) detected on Tomato.",
    detected_crop="Tomato",
    crop_confidence=0.97,
    disease_label="early_blight",
    disease_name="Early Blight (Alternaria solani)",
    disease_confidence=0.91,
    severity="moderate",
    predictions=[
        PredictionItem(label="early_blight", display_name="Early Blight (Alternaria solani)", probability=0.91),
        PredictionItem(label="late_blight", display_name="Late Blight (Phytophthora infestans)", probability=0.05),
        PredictionItem(label="healthy", display_name="Healthy", probability=0.04),
    ],
    model_version="demo",
)

# ── Demo Irrigation ──────────────────────────────────────────────────────────
DEMO_IRRIGATION: list[IrrigationRecommendation] = [
    IrrigationRecommendation(
        field_id="field-01",
        field_name="Tomato Field A",
        crop="Tomato",
        water_stress="high",
        irrigation_required=True,
        estimated_duration_minutes=12,
        confidence=0.87,
        reasons=[
            "Soil moisture (42.5%) is below the 50% optimal threshold for fruiting stage",
            "Temperature elevated at 28.4°C — increases evapotranspiration rate",
            "Rainfall probability is below 10% for the next 48 hours",
            "Current growth stage (Fruiting) has high water demand",
        ],
        sensor_snapshot=SensorSnapshot(soil_moisture=42.5, temperature=28.4, humidity=65.0),
    ),
    IrrigationRecommendation(
        field_id="field-02",
        field_name="Apple Orchard B",
        crop="Apple",
        water_stress="medium",
        irrigation_required=True,
        estimated_duration_minutes=8,
        confidence=0.74,
        reasons=[
            "Soil moisture (29.1%) approaching lower threshold for fruit set stage",
            "High temperature (31.2°C) accelerating moisture loss",
            "No significant rainfall in past 7 days",
        ],
        sensor_snapshot=SensorSnapshot(soil_moisture=29.1, temperature=31.2, humidity=52.0),
    ),
    IrrigationRecommendation(
        field_id="field-03",
        field_name="Capsicum Field C",
        crop="Capsicum",
        water_stress="low",
        irrigation_required=False,
        estimated_duration_minutes=0,
        confidence=0.92,
        reasons=[
            "Soil moisture (68.3%) is within the optimal 50-70% range for capsicum",
            "Humidity is optimal at 74%",
            "Current flowering stage is adequately watered",
        ],
        sensor_snapshot=SensorSnapshot(soil_moisture=68.3, temperature=26.8, humidity=74.0),
    ),
    IrrigationRecommendation(
        field_id="field-04",
        field_name="Tomato Field D",
        crop="Tomato",
        water_stress="critical",
        irrigation_required=True,
        estimated_duration_minutes=25,
        confidence=0.96,
        reasons=[
            "CRITICAL: Soil moisture at 18.2% — severely below 45% threshold",
            "Extreme temperature stress at 33.5°C",
            "Sensor offline — last known reading 2+ hours ago indicates deteriorating conditions",
            "Flowering stage has high water demand",
        ],
        sensor_snapshot=SensorSnapshot(soil_moisture=18.2, temperature=33.5, humidity=44.0),
    ),
]

# ── Demo Yield ───────────────────────────────────────────────────────────────
DEMO_YIELD: list[YieldPrediction] = [
    YieldPrediction(
        crop="Tomato",
        field_id="field-01",
        field_name="Tomato Field A",
        estimated_yield_t_per_hectare=4.8,
        prediction_interval=PredictionInterval(lower=4.4, upper=5.2),
        confidence=0.82,
        last_season_yield=4.2,
        factors=[
            YieldFactor(name="Soil Moisture", impact="positive", weight=0.85),
            YieldFactor(name="Temperature", impact="negative", weight=0.72),
            YieldFactor(name="Fertilization", impact="positive", weight=0.91),
            YieldFactor(name="Disease Pressure", impact="negative", weight=0.45),
            YieldFactor(name="Irrigation History", impact="positive", weight=0.78),
        ],
    ),
    YieldPrediction(
        crop="Apple",
        field_id="field-02",
        field_name="Apple Orchard B",
        estimated_yield_t_per_hectare=12.6,
        prediction_interval=PredictionInterval(lower=11.4, upper=13.8),
        confidence=0.71,
        last_season_yield=13.1,
        factors=[
            YieldFactor(name="Soil Moisture", impact="negative", weight=0.62),
            YieldFactor(name="Temperature", impact="negative", weight=0.68),
            YieldFactor(name="Fertilization", impact="neutral", weight=0.55),
            YieldFactor(name="Disease Pressure", impact="negative", weight=0.38),
        ],
    ),
    YieldPrediction(
        crop="Capsicum",
        field_id="field-03",
        field_name="Capsicum Field C",
        estimated_yield_t_per_hectare=9.4,
        prediction_interval=PredictionInterval(lower=8.7, upper=10.1),
        confidence=0.88,
        last_season_yield=8.8,
        factors=[
            YieldFactor(name="Soil Moisture", impact="positive", weight=0.94),
            YieldFactor(name="Temperature", impact="positive", weight=0.82),
            YieldFactor(name="Fertilization", impact="positive", weight=0.89),
            YieldFactor(name="Disease Pressure", impact="neutral", weight=0.22),
        ],
    ),
]
