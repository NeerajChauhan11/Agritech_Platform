"""Knowledge-base and model-catalog consistency tests."""

from app.core.constants import CROP_DISPLAY_NAMES, CROP_PROFILES, SUPPORTED_CROPS
from app.core.model_catalog import CROP_ID_SPEC, DISEASE_MODEL_SPECS
from app.knowledge.disease_info import get_disease_info


def test_every_class_of_every_model_has_guidance() -> None:
    missing = [
        (crop, label)
        for crop, spec in DISEASE_MODEL_SPECS.items()
        for label in spec.classes
        if get_disease_info(crop, label) is None
    ]
    assert missing == []


def test_guidance_entries_are_complete() -> None:
    for crop, spec in DISEASE_MODEL_SPECS.items():
        for label in spec.classes:
            entry = get_disease_info(crop, label)
            assert entry and entry.display_name and entry.symptoms
            assert entry.treatment and entry.prevention
            assert (entry.severity == "none") == (label == "healthy")


def test_catalog_covers_exactly_the_three_supported_crops() -> None:
    expected = {"apple", "tomato", "capsicum"}
    assert SUPPORTED_CROPS == ("apple", "tomato", "capsicum")
    assert set(DISEASE_MODEL_SPECS) == set(CROP_DISPLAY_NAMES) == set(CROP_PROFILES) == expected
    assert set(CROP_ID_SPEC.classes) == expected | {"unknown"}
    assert len(CROP_ID_SPEC.classes) == len(expected) + 1
