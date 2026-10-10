"""Application constants, agronomic limits, and thresholds."""

from typing import Final

# API Metadata
API_V1_PREFIX: Final[str] = "/api/v1"

# Alert Definitions
ALERT_SEVERITIES: Final[tuple[str, ...]] = ("info", "warning", "critical")
ALERT_CATEGORIES: Final[tuple[str, ...]] = (
    "disease",
    "irrigation",
    "sensor",
    "weather",
    "yield",
)

# Field Status Definitions
FIELD_STATUSES: Final[tuple[str, ...]] = ("healthy", "warning", "critical")
DEVICE_STATUSES: Final[tuple[str, ...]] = ("online", "offline", "warning")

# Water Stress Levels
WATER_STRESS_LEVELS: Final[tuple[str, ...]] = (
    "low",
    "medium",
    "high",
    "critical",
)

# Agronomic Valid Ranges for Boundary Validation & Data Cleaning
SENSOR_BOUNDS: Final[dict[str, dict[str, float]]] = {
    "soil_moisture": {"min": 0.0, "max": 100.0, "default": 45.0},
    "temperature": {"min": -20.0, "max": 65.0, "default": 25.0},
    "humidity": {"min": 0.0, "max": 100.0, "default": 60.0},
    "ph_level": {"min": 0.0, "max": 14.0, "default": 6.8},
    "nitrogen": {"min": 0.0, "max": 300.0, "default": 40.0},
    "phosphorus": {"min": 0.0, "max": 200.0, "default": 25.0},
    "potassium": {"min": 0.0, "max": 300.0, "default": 35.0},
}

# Soil Moisture Thresholds for Irrigation Advisor (%)
SOIL_MOISTURE_CRITICAL_THRESHOLD: Final[float] = 20.0
SOIL_MOISTURE_WARNING_THRESHOLD: Final[float] = 35.0
SOIL_MOISTURE_OPTIMAL_MIN: Final[float] = 45.0
SOIL_MOISTURE_OPTIMAL_MAX: Final[float] = 75.0

# Temperature thresholds (°C)
TEMP_EXTREME_HEAT_THRESHOLD: Final[float] = 35.0
TEMP_EXTREME_COLD_THRESHOLD: Final[float] = 5.0

# ── Supported crops (single source of truth) ─────────────────────────────────
# Active development phase: only these crops are accepted anywhere in the API.
# Wheat, sugarcane and rice/paddy are deferred (their datasets are not accessible
# from Colab right now); see docs/models.md for what re-enabling them needs.
SUPPORTED_CROPS: Final[tuple[str, ...]] = ("apple", "tomato", "capsicum")
CROP_DISPLAY_NAMES: Final[dict[str, str]] = {
    "apple": "Apple",
    "tomato": "Tomato",
    "capsicum": "Capsicum",
}
# Alternative spellings -> canonical id. Applied after lower-casing and replacing
# spaces/hyphens with underscores.
CROP_ALIASES: Final[dict[str, str]] = {
    "pepper": "capsicum",
    "bell_pepper": "capsicum",
    "sweet_pepper": "capsicum",
    "pepper_bell": "capsicum",
}
CROP_NOT_SUPPORTED_CODE: Final[str] = "CROP_NOT_SUPPORTED"

# Crop Agronomic Profiles & Baselines. Approximate agronomic defaults for the
# irrigation and yield advisors, not measured data: review before production use.
CROP_PROFILES: Final[dict[str, dict[str, float]]] = {
    "tomato": {
        "moisture_min": 45.0,
        "moisture_max": 65.0,
        "base_yield": 4.5,
        "opt_temp": 24.0,
        "opt_n": 40.0,
        "opt_p": 25.0,
        "opt_k": 35.0,
    },
    "apple": {
        "moisture_min": 40.0,
        "moisture_max": 60.0,
        "base_yield": 12.0,
        "opt_temp": 22.0,
        "opt_n": 35.0,
        "opt_p": 22.0,
        "opt_k": 40.0,
    },
    "capsicum": {
        "moisture_min": 50.0,
        "moisture_max": 70.0,
        "base_yield": 9.0,
        "opt_temp": 25.0,
        "opt_n": 45.0,
        "opt_p": 28.0,
        "opt_k": 38.0,
    },
}

# ── Diagnosis pipeline ───────────────────────────────────────────────────────
DIAGNOSIS_TOP_K: Final[int] = 3

# Crop identification acceptance: top-1 probability and its margin over top-2.
CROP_CONFIDENCE_MIN: Final[float] = 0.70
CROP_MARGIN_MIN: Final[float] = 0.20
CROP_UNKNOWN_CLASS: Final[str] = "unknown"

# Below this top-1 disease probability the result is "disease_uncertain".
DISEASE_CONFIDENCE_MIN: Final[float] = 0.60

# General-category tier (zero-shot CLIP). Scores are relative, not calibrated probabilities, so
# a result is accepted only if the top category is clearly ahead; otherwise "disease_uncertain".
# 0.60 chosen on 189 public sample images: it cut wrong accepted categories from 6 to 2 versus 0.50.
# See docs/models.md "Inspection demo mode"; not validated on field data.
CATEGORY_CONFIDENCE_MIN: Final[float] = 0.60
CATEGORY_MARGIN_MIN: Final[float] = 0.15

# Image-quality gate (tunable; measured on a <=512px grayscale copy).
QUALITY_MIN_SIDE_PX: Final[int] = 224
QUALITY_BLUR_LAPLACIAN_MIN: Final[float] = 60.0
QUALITY_BRIGHTNESS_MIN: Final[float] = 40.0
QUALITY_BRIGHTNESS_MAX: Final[float] = 215.0
QUALITY_CLIPPED_MAX_FRACTION: Final[float] = 0.35
QUALITY_LEAF_COVERAGE_MIN: Final[float] = 0.12

# Human-readable outcome text: status -> (message, what the user should do).
DIAGNOSIS_STATUS_MESSAGES: Final[dict[str, tuple[str, str]]] = {
    "ok": ("Diagnosis complete.", ""),
    "low_quality_image": (
        "The image quality is too low to analyse.",
        "Retake a sharp, well-lit close-up of a single leaf.",
    ),
    "crop_uncertain": (
        "We could not tell which crop this leaf belongs to.",
        "Retake the photo as a close-up of a single leaf against a plain background.",
    ),
    "crop_unsupported": (
        "This crop is not supported yet.",
        f"Supported crops: {', '.join(CROP_DISPLAY_NAMES[c] for c in SUPPORTED_CROPS)}.",
    ),
    "model_unavailable": (
        "The disease model for this crop is not installed on the server.",
        "Ask the administrator to install the model weights (see docs/models.md).",
    ),
    "disease_uncertain": (
        "The model is not confident enough to name a disease.",
        (
            "Retake a sharper close-up of the affected area, or consult an agronomist. "
            "The candidates below are possibilities, not a diagnosis."
        ),
    ),
}

# Image-quality issue code -> (message, what the user should do).
QUALITY_ISSUE_MESSAGES: Final[dict[str, tuple[str, str]]] = {
    "unreadable": ("The image could not be read.", "Upload a JPG, PNG or WebP photo."),
    "low_resolution": (
        "The image resolution is too low.",
        f"Use a photo of at least {QUALITY_MIN_SIDE_PX}x{QUALITY_MIN_SIDE_PX} pixels.",
    ),
    "blurry": ("The image is blurry.", "Hold the camera steady and tap to focus, then retake the photo."),
    "too_dark": ("The image is too dark.", "Retake the photo in daylight or with better lighting."),
    "too_bright": ("The image is overexposed.", "Retake the photo out of direct glare or harsh sunlight."),
    "no_leaf": (
        "No leaf was found in the image.",
        "Retake the photo closer, with a single leaf filling most of the frame.",
    ),
}
