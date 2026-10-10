"""Tests for the torch-free parts of scripts/train_disease_model.py."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "train_disease_model.py"


@pytest.fixture(scope="module")
def trainer():
    spec = importlib.util.spec_from_file_location("train_disease_model", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_handles_plantvillage_names(trainer) -> None:
    assert trainer.normalize("Tomato___Early_blight") == "early_blight"
    assert trainer.normalize("Tomato___Leaf_Mold") == "leaf_mold"
    assert trainer.normalize("Apple Scab-Leaf") == "apple_scab_leaf"


def test_crop_prefix_filter(trainer) -> None:
    assert trainer.crop_prefix_matches("Tomato___healthy", "tomato")
    assert not trainer.crop_prefix_matches("Potato___healthy", "tomato")
    assert trainer.crop_prefix_matches("Pepper,_bell___healthy", "capsicum")  # alias of the canonical id
    assert not trainer.crop_prefix_matches("Pepper,_bell___healthy", "tomato")
    assert trainer.crop_prefix_matches("Apple___Apple_scab", "apple")
    assert trainer.crop_prefix_matches("brown_spot", "apple")  # plain folders always match


def test_stratified_split_keeps_every_class_in_both_sets(trainer) -> None:
    labels = [0] * 10 + [1] * 5 + [2] * 2
    train, val = trainer.stratified_split(labels, 0.2, seed=1)
    assert sorted(train + val) == list(range(len(labels)))
    assert not set(train) & set(val)
    for cls in (0, 1, 2):
        assert any(labels[i] == cls for i in train)
        assert any(labels[i] == cls for i in val)


def test_stratified_split_is_reproducible_and_rejects_tiny_classes(trainer) -> None:
    labels = [0] * 6 + [1] * 6
    assert trainer.stratified_split(labels, 0.25, 7) == trainer.stratified_split(labels, 0.25, 7)
    with pytest.raises(ValueError):
        trainer.stratified_split([0, 0, 1], 0.2, 1)


def test_compute_metrics(trainer) -> None:
    y_true = [0, 0, 0, 1, 1, 2]
    y_pred = [0, 0, 1, 1, 1, 0]
    m = trainer.compute_metrics(y_true, y_pred, ["a", "b", "c"])
    assert m["accuracy"] == pytest.approx(4 / 6, abs=1e-4)
    assert m["confusion_matrix"]["matrix"] == [[2, 1, 0], [0, 2, 0], [1, 0, 0]]
    assert m["per_class"]["a"]["recall"] == pytest.approx(2 / 3, abs=1e-4)
    assert m["per_class"]["b"]["precision"] == pytest.approx(2 / 3, abs=1e-4)
    assert m["per_class"]["c"]["f1"] == 0.0
    assert m["per_class"]["a"]["support"] == 3


def test_collect_samples_fails_loudly_on_class_mismatch(trainer, tmp_path: Path) -> None:
    from app.core.model_catalog import DISEASE_MODEL_SPECS

    (tmp_path / "Pepper,_bell___Bacterial_spot").mkdir()
    (tmp_path / "Pepper,_bell___Bacterial_spot" / "a.jpg").write_bytes(b"x")
    (tmp_path / "Pepper,_bell___Mystery").mkdir()
    with pytest.raises(SystemExit, match="does not match the catalog"):
        trainer.collect_samples(tmp_path, DISEASE_MODEL_SPECS["capsicum"], "capsicum", trainer.BUILTIN_ALIASES)


def test_resolve_spec_accepts_supported_crops_and_aliases(trainer) -> None:
    from types import SimpleNamespace

    for given, canonical in (("tomato", "tomato"), ("Apple", "apple"), ("pepper", "capsicum")):
        args = SimpleNamespace(mode="disease", crop=given)
        assert trainer.resolve_spec(args).key == canonical
        assert args.crop == canonical


@pytest.mark.parametrize("crop", ["wheat", "sugarcane", "rice", "potato", "corn", None])
def test_resolve_spec_rejects_out_of_scope_crops(trainer, crop) -> None:
    from types import SimpleNamespace

    with pytest.raises(SystemExit, match="apple, tomato, capsicum"):
        trainer.resolve_spec(SimpleNamespace(mode="disease", crop=crop))
