"""Types and constructors shared by the per-crop disease knowledge modules."""

from dataclasses import dataclass

from app.schemas.diagnosis import Severity

HEALTHY_TREATMENT = ("No treatment needed.",)


@dataclass(frozen=True)
class DiseaseInfo:
    """Farmer-facing description of one diagnosable condition."""

    display_name: str
    severity: Severity
    symptoms: tuple[str, ...]
    treatment: tuple[str, ...]
    prevention: tuple[str, ...]


def info(
    name: str,
    severity: Severity,
    symptoms: tuple[str, ...],
    treatment: tuple[str, ...],
    prevention: tuple[str, ...],
) -> DiseaseInfo:
    """Short constructor used by the per-crop data modules."""
    return DiseaseInfo(name, severity, symptoms, treatment, prevention)


def healthy(prevention: tuple[str, ...]) -> DiseaseInfo:
    """Entry for a healthy-leaf class."""
    return DiseaseInfo(
        "Healthy",
        "none",
        ("No disease symptoms detected on the leaf.",),
        HEALTHY_TREATMENT,
        prevention,
    )
