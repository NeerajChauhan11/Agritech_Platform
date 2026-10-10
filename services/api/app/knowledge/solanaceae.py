"""Disease knowledge for tomato and capsicum (Solanaceae)."""

from app.knowledge.models import DiseaseInfo, healthy, info

_EARLY_BLIGHT = info(
    "Early Blight (Alternaria solani)",
    "moderate",
    (
        "Dark brown spots with concentric rings (target-like) on older leaves.",
        "Yellowing of tissue around the spots; affected leaves may drop.",
    ),
    (
        "Remove and destroy heavily affected lower leaves.",
        "Apply a protectant fungicide registered for the crop (e.g. chlorothalonil, mancozeb or copper), following the label.",
    ),
    (
        "Rotate away from tomato, capsicum and other Solanaceae crops for 2-3 seasons.",
        "Mulch the soil, water at the base, and avoid wetting the foliage.",
        "Keep plants well spaced and fed so they are not stressed.",
    ),
)

_LATE_BLIGHT = info(
    "Late Blight (Phytophthora infestans)",
    "high",
    (
        "Large, greasy, water-soaked blotches that turn brown; white mould on the underside in humid weather.",
        "Firm brown rot on fruit or tubers. Spreads very fast in cool, wet conditions.",
    ),
    (
        "Act immediately: remove and destroy infected plants (do not compost them).",
        "Apply a fungicide effective against oomycetes, following the label and local extension advice.",
    ),
    (
        "Plant resistant varieties and certified disease-free seed or tubers.",
        "Avoid long leaf wetness; remove volunteer plants and cull piles; scout during cool, humid weather.",
    ),
)

_BACTERIAL_SPOT = info(
    "Bacterial Spot (Xanthomonas)",
    "moderate",
    (
        "Small water-soaked spots that turn dark brown, often with a yellow halo.",
        "Spots may fall out, leaving a shot-hole look; rough scabby spots on fruit.",
    ),
    (
        "Remove badly affected leaves or plants; do not handle plants while wet.",
        "Copper-based bactericide programmes can slow spread; follow the label.",
    ),
    (
        "Use certified disease-free seed and transplants.",
        "Rotate crops, use drip irrigation, and disinfect tools.",
    ),
)

SOLANACEAE_INFO: dict[tuple[str, str], DiseaseInfo] = {
    ("tomato", "bacterial_spot"): _BACTERIAL_SPOT,
    ("tomato", "early_blight"): _EARLY_BLIGHT,
    ("tomato", "late_blight"): _LATE_BLIGHT,
    ("tomato", "leaf_mold"): info(
        "Leaf Mold (Passalora fulva)",
        "moderate",
        (
            "Pale green to yellow spots on the upper leaf surface.",
            "Olive-green to brown velvety mould on the underside; common in humid, poorly ventilated crops.",
        ),
        (
            "Lower humidity and improve ventilation; remove infected leaves.",
            "Apply a registered fungicide if the disease keeps spreading, following the label.",
        ),
        (
            "Choose resistant varieties and keep good spacing.",
            "Avoid wetting foliage and sanitise greenhouse structures between crops.",
        ),
    ),
    ("tomato", "septoria_leaf_spot"): info(
        "Septoria Leaf Spot (Septoria lycopersici)",
        "moderate",
        (
            "Many small circular spots with dark margins and grey-white centres, starting on lower leaves.",
            "Tiny black dots may be visible in the spot centres.",
        ),
        (
            "Remove infected lower leaves.",
            "Apply a protectant fungicide (e.g. chlorothalonil, copper or mancozeb), following the label.",
        ),
        (
            "Rotate crops for 2-3 seasons and remove crop debris.",
            "Mulch and use drip irrigation to avoid splashing soil onto leaves.",
        ),
    ),
    ("tomato", "spider_mites"): info(
        "Spider Mites (two-spotted spider mite)",
        "moderate",
        (
            "Fine yellow stippling on leaves, later bronzing and drying.",
            "Fine webbing on the underside of leaves, worst in hot, dry weather.",
        ),
        (
            "Spray the leaf undersides with water, insecticidal soap or horticultural oil.",
            "Use a registered miticide if infestations persist, following the label.",
        ),
        (
            "Avoid water stress and dusty conditions.",
            "Scout leaf undersides early and protect natural enemies by avoiding broad-spectrum insecticides.",
        ),
    ),
    ("tomato", "target_spot"): info(
        "Target Spot (Corynespora cassiicola)",
        "moderate",
        (
            "Brown spots with concentric rings and a yellow halo on leaves; can also affect stems and fruit.",
            "Looks similar to early blight.",
        ),
        (
            "Remove infected leaves.",
            "Apply a registered fungicide, following the label.",
        ),
        (
            "Improve airflow with wider spacing and pruning.",
            "Avoid overhead irrigation and rotate crops.",
        ),
    ),
    ("tomato", "yellow_leaf_curl_virus"): info(
        "Tomato Yellow Leaf Curl Virus",
        "high",
        (
            "Upward curling and yellowing of leaf margins, stunted growth.",
            "Flower drop and poor fruit set. Spread by whiteflies.",
        ),
        (
            "There is no cure: remove and destroy infected plants early.",
            "Control whiteflies with yellow sticky traps, soap/neem sprays or registered insecticides rotated by mode of action.",
        ),
        (
            "Use resistant or tolerant varieties and virus-free transplants.",
            "Protect nurseries with insect-proof nets, use reflective mulch, and remove weed hosts.",
        ),
    ),
    ("tomato", "mosaic_virus"): info(
        "Tomato Mosaic Virus",
        "high",
        (
            "Light and dark green mottled (mosaic) pattern on leaves; distorted or fern-like leaves.",
            "Stunting and uneven fruit ripening.",
        ),
        (
            "There is no cure: remove and destroy infected plants.",
            "Wash hands and disinfect tools after handling affected plants.",
        ),
        (
            "Use resistant varieties and certified seed.",
            "Control weeds, keep tools clean, and do not handle tobacco before touching plants.",
        ),
    ),
    ("tomato", "healthy"): healthy(("Keep scouting weekly and maintain balanced nutrition and irrigation.",)),
    ("capsicum", "bacterial_spot"): _BACTERIAL_SPOT,
    ("capsicum", "healthy"): healthy(("Keep scouting weekly and avoid working among wet plants.",)),
}
