"""Tests for the offline parts of scripts/prepare_datasets.py (no downloads)."""

import importlib.util
import sys
from collections import Counter
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"


@pytest.fixture(scope="module")
def prep():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("prepare_datasets", SCRIPTS / "prepare_datasets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_images(folder: Path, count: int) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        (folder / f"img{i}.jpg").write_bytes(b"x")


def test_deferred_crop_sources_are_gone(prep) -> None:
    assert set(prep.ALL_SOURCES) == {"plantvillage", "plantdoc", "negatives", "crop_id"}
    for name in ("KEYWORD_RULES", "MENDELEY_SETS", "ZENODO_WHEAT_API", "prepare_keyword_dataset", "zenodo_wheat_url"):
        assert not hasattr(prep, name), name


def test_dataset_crops_are_exactly_the_supported_crops(prep) -> None:
    from app.core.constants import SUPPORTED_CROPS

    assert set(prep.PLANTVILLAGE_CROPS.values()) == set(SUPPORTED_CROPS)
    assert {crop for crop, _ in prep.PLANTDOC_MAP.values()} == set(SUPPORTED_CROPS)


def test_unknown_source_is_rejected(prep, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="wheat"):
        prep.main(["--out-dir", str(tmp_path), "--only", "wheat"])


def test_unreachable_source_fails_with_a_clear_message(prep, tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="Dataset source unavailable"):
        prep.fetch_git(str(tmp_path / "does-not-exist"), tmp_path / "clone")


def test_prepare_plantvillage_maps_crops_and_collects_unknown(prep, tmp_path: Path) -> None:
    raw, out = tmp_path / "color", tmp_path / "disease"
    _make_images(raw / "Tomato___Tomato_Yellow_Leaf_Curl_Virus", 2)
    _make_images(raw / "Tomato___Spider_mites Two-spotted_spider_mite", 2)
    _make_images(raw / "Pepper,_bell___healthy", 3)
    _make_images(raw / "Potato___Early_blight", 2)
    _make_images(raw / "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", 2)
    _make_images(raw / "Grape___healthy", 5)
    counts: Counter = Counter()
    unknown: list[Path] = []
    prep.prepare_plantvillage(raw, out, counts, unknown)
    assert counts[("tomato", "yellow_leaf_curl_virus")] == 2
    assert counts[("tomato", "spider_mites")] == 2
    assert counts[("capsicum", "healthy")] == 3
    assert (out / "capsicum" / "healthy").is_dir() and not (out / "pepper").exists()
    assert set(out.iterdir()) == {out / "tomato", out / "capsicum"}  # no folder for unsupported crops
    assert len(unknown) == 9  # potato (2), corn (2) and grape (5) become "unknown" negatives


def test_plantdoc_map_targets_valid_catalog_classes(prep) -> None:
    from app.core.model_catalog import DISEASE_MODEL_SPECS

    for crop, cls in prep.PLANTDOC_MAP.values():
        assert cls in DISEASE_MODEL_SPECS[crop].classes


def test_build_crop_id_prefers_field_photos_and_caps(prep, tmp_path: Path) -> None:
    disease, out = tmp_path / "disease", tmp_path / "crop_id"
    folder = disease / "tomato" / "healthy"
    folder.mkdir(parents=True)
    for i in range(5):
        (folder / f"pv_healthy_{i}.jpg").write_bytes(b"x")
    for i in range(2):
        (folder / f"pd_train_healthy_{i}.jpg").write_bytes(b"x")
    pool = [tmp_path / f"u{i}.jpg" for i in range(4)]
    for path in pool:
        path.write_bytes(b"x")
    prep.build_crop_id(disease, pool, out, max_per_crop=3, seed=1)
    names = sorted(f.name for f in (out / "tomato").iterdir())
    assert len(names) == 3
    assert len(list((out / "unknown").iterdir())) == 3
