"""Disease knowledge for apple."""

from app.knowledge.models import DiseaseInfo, healthy, info

ORCHARD_INFO: dict[tuple[str, str], DiseaseInfo] = {
    ("apple", "apple_scab"): info(
        "Apple Scab (Venturia inaequalis)",
        "moderate",
        (
            "Olive-green to brown velvety spots on leaves; leaves may yellow and drop early.",
            "Dark, corky, scabby lesions on fruit.",
        ),
        (
            "Apply a protectant or systemic fungicide programme from green tip through petal fall, following the label.",
            "Rake and destroy fallen leaves.",
        ),
        (
            "Plant scab-resistant cultivars.",
            "Prune for an open canopy so leaves dry quickly, and manage leaf litter each autumn.",
        ),
    ),
    ("apple", "black_rot"): info(
        "Black Rot (Botryosphaeria obtusa)",
        "moderate",
        (
            "Purple-bordered 'frogeye' leaf spots.",
            "Fruit rots turn black and mummify; cankers form on branches.",
        ),
        (
            "Prune out cankers and dead wood and remove mummified fruit.",
            "Apply a registered fungicide during the growing season, following the label.",
        ),
        (
            "Avoid wounding trees and keep them vigorous with balanced nutrition.",
            "Remove dead wood and fruit debris every season.",
        ),
    ),
    ("apple", "cedar_apple_rust"): info(
        "Cedar-Apple Rust (Gymnosporangium juniperi-virginianae)",
        "moderate",
        (
            "Bright yellow-orange spots on leaves, with small tube-like structures on the underside.",
            "Lesions can also form on fruit.",
        ),
        (
            "Apply a registered fungicide from pink bud to petal fall, following the label.",
            "Remove nearby galls where practical.",
        ),
        (
            "Plant resistant cultivars.",
            "Remove nearby juniper or red cedar hosts where practical.",
        ),
    ),
    ("apple", "healthy"): healthy(("Maintain pruning, sanitation and a monitoring routine through the season.",)),
}
