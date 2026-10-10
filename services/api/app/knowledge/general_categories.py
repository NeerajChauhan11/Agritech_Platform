"""Guidance for the general-category tier: plain-language advice per (crop, category).

Category advice is deliberately generic: it contains no product names or dosages and always
defers to local agronomists for confirmation. Examples are well-documented diseases of each
crop, used for explanation only; the tier never claims any of them as a diagnosis.
"""

from dataclasses import dataclass
from typing import Final

from app.core.constants import SUPPORTED_CROPS
from app.core.general_catalog import GENERAL_CATEGORIES


@dataclass(frozen=True)
class CategoryGuidance:
    """What a farmer should know about one coarse category on one crop."""

    description: str
    look_for: tuple[str, ...]
    actions: tuple[str, ...]
    prevention: tuple[str, ...]
    consult: str


_BASE: Final[dict[str, dict[str, tuple[str, ...] | str]]] = {
    "healthy": {
        "description": "The leaf shows no clear signs of disease, pests or stress in this photo.",
        "look_for": ("Even green colour", "No spots, holes, curling or discolouration"),
        "actions": ("No treatment needed.", "Keep monitoring; photograph a few more leaves, including older ones."),
        "prevention": ("Scout regularly", "Keep irrigation, spacing and field hygiene consistent"),
        "consult": "Consult an agronomist if the plant looks unwell despite a healthy leaf photo.",
    },
    "fungal": {
        "description": "The pattern looks like a fungal leaf problem, which spreads in humid, wet conditions.",
        "look_for": ("Brown, grey or black spots, often with rings or halos", "Powdery or fuzzy growth", "Rust-coloured pustules"),
        "actions": (
            "Remove and bin badly affected leaves; do not compost them.",
            "Avoid overhead watering and handling plants while wet.",
            "Ask your local extension service which fungicide, if any, is approved for this crop.",
        ),
        "prevention": ("Improve airflow with spacing and pruning", "Water at the base, early in the day", "Rotate crops and clear fallen debris"),
        "consult": "Consult an agronomist if spots spread to new leaves within a week or reach the fruit.",
    },
    "bacterial": {
        "description": "The pattern looks like a bacterial problem, which spreads through splashing water and tools.",
        "look_for": ("Small water-soaked or angular spots", "Dark spots with yellow halos", "Spots that turn brown and may drop out"),
        "actions": (
            "Remove affected leaves and disinfect pruning tools between plants.",
            "Avoid working in the crop or irrigating overhead while foliage is wet.",
            "Ask your local extension service about approved bacterial-disease options.",
        ),
        "prevention": ("Use clean seed and healthy planting material", "Drip irrigation instead of sprinklers", "Rotate crops"),
        "consult": "Consult an agronomist quickly if the spots are spreading, as bacterial diseases can move fast.",
    },
    "viral": {
        "description": "The pattern looks like a possible virus, which cannot be cured and is spread by insects, tools or hands.",
        "look_for": ("Mosaic of light and dark green patches", "Leaf curling, puckering or distortion", "Stunted growth and yellowing"),
        "actions": (
            "Isolate or remove clearly affected plants to protect neighbours.",
            "Control sap-sucking insects such as whiteflies and aphids that carry viruses.",
            "Wash hands and disinfect tools after handling affected plants.",
        ),
        "prevention": ("Use virus-free or resistant planting material", "Control insect vectors early", "Remove weeds that host viruses"),
        "consult": "Consult an agronomist to confirm: nutrient problems and herbicide drift can look similar.",
    },
    "pest": {
        "description": "The damage looks like it was caused by chewing or sap-sucking pests such as insects or mites.",
        "look_for": ("Holes or chewed edges", "Fine speckling or stippling, webbing", "Tunnels or trails inside the leaf, sticky residue"),
        "actions": (
            "Inspect the underside of leaves and growing tips for insects, mites or eggs.",
            "Remove heavily damaged leaves and wash off light infestations where practical.",
            "Ask your local extension service about approved, targeted pest control for this crop.",
        ),
        "prevention": ("Scout weekly", "Protect natural predators", "Avoid excess nitrogen and keep plants well watered"),
        "consult": "Consult an agronomist if pests are found in numbers or damage appears on new growth.",
    },
    "nutrient_stress": {
        "description": "The discolouration looks like nutrient deficiency or environmental stress rather than infection.",
        "look_for": ("Yellowing between veins or on older leaves", "Scorched or dry leaf edges", "Purple or pale tints and slow growth"),
        "actions": (
            "Check irrigation, drainage and recent weather for water, heat or salt stress.",
            "Consider a soil or leaf-tissue test before adding any fertiliser.",
            "Correct the cause gradually; over-fertilising can cause further damage.",
        ),
        "prevention": ("Soil-test before each season", "Maintain even moisture and suitable soil pH", "Follow a balanced fertiliser plan"),
        "consult": "Consult an agronomist if yellowing spreads to new leaves or a soil test is inconclusive.",
    },
}

# Well-documented examples per (crop, category), for explanation only.
_EXAMPLES: Final[dict[tuple[str, str], tuple[str, ...]]] = {
    ("apple", "fungal"): ("apple scab", "cedar apple rust", "powdery mildew"),
    ("apple", "bacterial"): ("fire blight",),
    ("apple", "viral"): ("apple mosaic virus",),
    ("apple", "pest"): ("spider mites", "aphids", "leaf miners"),
    ("apple", "nutrient_stress"): ("iron or magnesium deficiency", "potassium-related leaf scorch"),
    ("tomato", "fungal"): ("early blight", "late blight", "leaf mold", "Septoria leaf spot"),
    ("tomato", "bacterial"): ("bacterial spot", "bacterial speck"),
    ("tomato", "viral"): ("tomato yellow leaf curl virus", "tomato mosaic virus"),
    ("tomato", "pest"): ("spider mites", "whiteflies", "leaf miners"),
    ("tomato", "nutrient_stress"): ("magnesium deficiency", "nitrogen deficiency"),
    ("capsicum", "fungal"): ("Cercospora leaf spot", "powdery mildew"),
    ("capsicum", "bacterial"): ("bacterial leaf spot",),
    ("capsicum", "viral"): ("cucumber mosaic virus", "tobamovirus mosaic"),
    ("capsicum", "pest"): ("aphids", "thrips", "mites"),
    ("capsicum", "nutrient_stress"): ("nitrogen deficiency", "magnesium deficiency"),
}


def get_category_guidance(crop: str, category: str) -> CategoryGuidance | None:
    """Guidance for (crop, category), or None for an unknown pair."""
    base = _BASE.get(category)
    if base is None or crop not in SUPPORTED_CROPS:
        return None
    description = str(base["description"])
    examples = _EXAMPLES.get((crop, category))
    if examples:
        description += f" Examples on this crop include {', '.join(examples)} (not confirmed here)."
    return CategoryGuidance(
        description=description,
        look_for=tuple(base["look_for"]),
        actions=tuple(base["actions"]),
        prevention=tuple(base["prevention"]),
        consult=str(base["consult"]),
    )


assert set(_BASE) == set(GENERAL_CATEGORIES), "guidance out of sync with GENERAL_CATEGORIES"
