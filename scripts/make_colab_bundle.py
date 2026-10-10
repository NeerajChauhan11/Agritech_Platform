#!/usr/bin/env python
"""Zip the few files Google Colab needs to prepare data and train the models.

  python scripts/make_colab_bundle.py      # writes agrismart_colab_bundle.zip in the repo root

Upload the zip to Colab (notebooks/train_models_colab.ipynb does this for you). The
bundle keeps the repo layout so the scripts find the class catalog unchanged.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE_FILES = [
    "scripts/train_disease_model.py",
    "scripts/prepare_datasets.py",
    "scripts/requirements-train.txt",
    "services/api/app/__init__.py",
    "services/api/app/core/__init__.py",
    "services/api/app/core/constants.py",
    "services/api/app/core/crops.py",
    "services/api/app/core/model_catalog.py",
]


def build(output: Path) -> Path:
    missing = [name for name in BUNDLE_FILES if not (ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Cannot build bundle, missing files: {missing}")
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in BUNDLE_FILES:
            archive.write(ROOT / name, name)
    return output


if __name__ == "__main__":
    path = build(ROOT / "agrismart_colab_bundle.zip")
    print(f"Wrote {path} ({path.stat().st_size / 1024:.0f} KB)")
