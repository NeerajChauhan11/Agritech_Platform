"""Disease knowledge base: symptoms, treatment and prevention per crop + class.

Guidance is general agronomic advice. It always defers to product labels and
local extension services for specific chemicals, rates and timings.
"""

from app.knowledge.models import DiseaseInfo
from app.knowledge.orchard import ORCHARD_INFO
from app.knowledge.solanaceae import SOLANACEAE_INFO

_KNOWLEDGE: dict[tuple[str, str], DiseaseInfo] = {
    **SOLANACEAE_INFO,
    **ORCHARD_INFO,
}


def get_disease_info(crop: str, label: str) -> DiseaseInfo | None:
    """Return the entry for (crop, class), or None if it is not documented."""
    return _KNOWLEDGE.get((crop, label))
