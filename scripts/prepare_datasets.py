#!/usr/bin/env python
"""Download public datasets and arrange them for scripts/train_disease_model.py.

Active scope: apple, tomato and capsicum only (see SUPPORTED_CROPS in
services/api/app/core/constants.py). Produces, under --out-dir (default ./data):

  disease/<crop>/<class>/*.jpg   one training folder per supported crop
  crop_id/<crop>/*.jpg           crop-identifier training set, balanced per crop
  crop_id/unknown/*.jpg          negatives: other plant species (incl. unsupported crops such as
                                 potato and corn) + generic non-plant photos

Sources: PlantVillage and PlantDoc (GitHub clones). Wheat, sugarcane and rice/paddy are deferred
because their datasets are not currently accessible; see docs/models.md.

Dataset locations are configurable (a git URL or a local path to an existing clone):

  AGRISMART_PLANTVILLAGE_SRC   default https://github.com/spMohanty/PlantVillage-Dataset
  AGRISMART_PLANTDOC_SRC       default https://github.com/pratikkayal/PlantDoc-Dataset

A missing or unreachable dataset stops the run with a clear message; nothing is substituted.
ALWAYS read the per-class summary printed at the end.

  python scripts/prepare_datasets.py                     # everything
  python scripts/prepare_datasets.py --only plantvillage,plantdoc
"""

from __future__ import annotations

import argparse
import hashlib
import os
import random
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "services" / "api"))

from app.core.model_catalog import CROP_ID_SPEC, DISEASE_MODEL_SPECS
from train_disease_model import BUILTIN_ALIASES, IMAGE_SUFFIXES, normalize

PLANTVILLAGE_SRC = os.environ.get("AGRISMART_PLANTVILLAGE_SRC", "https://github.com/spMohanty/PlantVillage-Dataset")
PLANTDOC_SRC = os.environ.get("AGRISMART_PLANTDOC_SRC", "https://github.com/pratikkayal/PlantDoc-Dataset")
ALL_SOURCES = ("plantvillage", "plantdoc", "negatives", "crop_id")

# PlantVillage folder prefix (normalised) -> crop key. Any other prefix (potato, corn, grape, ...)
# is a non-supported crop and becomes an "unknown" example for the crop identifier.
PLANTVILLAGE_CROPS = {"tomato": "tomato", "pepper_bell": "capsicum", "apple": "apple"}

# PlantDoc train/test folder (lower-case) -> (crop, class). Any other folder is another plant
# species and is used as "unknown" for the crop identifier. Class names are our best reading of
# PlantDoc's labels: check them if accuracy is poor.
PLANTDOC_MAP = {
    "apple scab leaf": ("apple", "apple_scab"), "apple leaf": ("apple", "healthy"),
    "apple rust leaf": ("apple", "cedar_apple_rust"),
    "bell_pepper leaf spot": ("capsicum", "bacterial_spot"), "bell_pepper leaf": ("capsicum", "healthy"),
    "tomato early blight leaf": ("tomato", "early_blight"), "tomato septoria leaf spot": ("tomato", "septoria_leaf_spot"),
    "tomato leaf bacterial spot": ("tomato", "bacterial_spot"), "tomato leaf late blight": ("tomato", "late_blight"),
    "tomato leaf mosaic virus": ("tomato", "mosaic_virus"), "tomato leaf yellow virus": ("tomato", "yellow_leaf_curl_virus"),
    "tomato leaf": ("tomato", "healthy"), "tomato mold leaf": ("tomato", "leaf_mold"),
    "tomato two spotted spider mites leaf": ("tomato", "spider_mites"),
}


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("  $", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def images_in(directory: Path) -> list[Path]:
    return [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_SUFFIXES]


def place(files: list[Path], dest_dir: Path, tag: str) -> int:
    """Copy files into dest_dir. Names derive from the source path, so same-named folders
    never collide and re-running the script does not create duplicates."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        digest = hashlib.md5(str(src).encode(), usedforsecurity=False).hexdigest()[:12]
        shutil.copy2(src, dest_dir / f"{tag}_{digest}{src.suffix.lower()}")
    return len(files)


def prepare_plantvillage(raw: Path, disease_root: Path, counts: Counter, unknown_pool: list[Path]) -> None:
    for folder in sorted(p for p in raw.iterdir() if p.is_dir() and "___" in p.name):
        prefix, _, label = folder.name.partition("___")
        crop = PLANTVILLAGE_CROPS.get(re.sub(r"[^a-z0-9]+", "_", prefix.lower()).strip("_"))
        if crop is None:
            unknown_pool.extend(images_in(folder))
            continue
        key = normalize(label)
        key = BUILTIN_ALIASES.get(key, key)
        if key not in DISEASE_MODEL_SPECS[crop].classes:
            print(f"  skipped PlantVillage folder '{folder.name}': not a {crop} catalog class")
            continue
        counts[(crop, key)] += place(images_in(folder), disease_root / crop / key, f"pv_{key}")


def prepare_plantdoc(repo: Path, disease_root: Path, counts: Counter, unknown_pool: list[Path]) -> None:
    for split in ("train", "test"):
        for folder in sorted(p for p in (repo / split).iterdir() if p.is_dir()):
            mapped = PLANTDOC_MAP.get(folder.name.lower())
            if mapped is None:
                unknown_pool.extend(images_in(folder))
                continue
            crop, cls = mapped
            counts[(crop, cls)] += place(images_in(folder), disease_root / crop / cls, f"pd_{split}_{cls}")


def fetch_negatives(dest: Path, limit: int) -> list[Path]:
    """Generic non-plant photos (textures, flowers) used as 'unknown' examples."""
    from torchvision import datasets

    dest.mkdir(parents=True, exist_ok=True)
    found: list[Path] = []
    for name, factory in (("dtd", lambda r: datasets.DTD(r, split="train", download=True)),
                          ("flowers", lambda r: datasets.Flowers102(r, split="train", download=True))):
        dataset = factory(str(dest / name))
        picks = random.sample(range(len(dataset)), min(limit, len(dataset)))
        for i in picks:
            path = dest / f"{name}_{i}.jpg"
            dataset[i][0].convert("RGB").save(path)
            found.append(path)
    return found


def build_crop_id(disease_root: Path, unknown_pool: list[Path], out_dir: Path, max_per_crop: int, seed: int) -> None:
    rng = random.Random(seed)
    for crop in DISEASE_MODEL_SPECS:
        files = sorted(f for f in (disease_root / crop).rglob("*") if f.suffix.lower() in IMAGE_SUFFIXES)
        # Field-style photos (PlantDoc, "pd_") first so they survive the per-crop cap.
        field_first = [f for f in files if f.name.startswith("pd_")] + [f for f in files if not f.name.startswith("pd_")]
        chosen = field_first[:max_per_crop]
        print(f"  crop_id/{crop}: {place(chosen, out_dir / crop, crop)} images")
    rng.shuffle(unknown_pool)
    print(f"  crop_id/unknown: {place(unknown_pool[:max_per_crop], out_dir / 'unknown', 'unk')} images")


def print_report(disease_root: Path) -> None:
    print("\n=== Per-class image counts (check every crop is complete) ===")
    for crop, spec in DISEASE_MODEL_SPECS.items():
        row = {cls: len(images_in(disease_root / crop / cls)) if (disease_root / crop / cls).exists() else 0
               for cls in spec.classes}
        missing = [c for c, n in row.items() if n < 20]
        status = "OK" if not missing else f"INCOMPLETE (fewer than 20 images: {missing})"
        print(f"{crop:10s} {status}\n           {row}")


def fetch_git(url: str, dest: Path, sparse: str | None = None) -> Path:
    """Clone `url` (a git URL or a local clone path) into `dest`; stop with a clear message on failure."""
    if dest.exists():
        return dest
    try:
        if sparse:
            run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest)])
            run(["git", "sparse-checkout", "set", sparse], cwd=dest)
        else:
            run(["git", "clone", "--depth", "1", url, str(dest)])
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise SystemExit(
            f"Dataset source unavailable: could not clone '{url}' ({exc}).\n"
            "Point AGRISMART_PLANTVILLAGE_SRC / AGRISMART_PLANTDOC_SRC at a reachable git URL or a local clone."
        ) from exc
    return dest


def require_dir(path: Path, what: str) -> Path:
    if not path.is_dir():
        raise SystemExit(f"Dataset layout not as expected: {what} not found at {path}.")
    return path


def load_unknown_pool(raw: Path) -> list[Path]:
    """Paths of non-crop images collected by earlier runs (so stages can run separately)."""
    pool_file = raw / "unknown_pool.txt"
    if not pool_file.exists():
        return []
    return [Path(line) for line in pool_file.read_text(encoding="utf-8").splitlines() if line]


def save_unknown_pool(raw: Path, pool: list[Path]) -> None:
    merged = sorted({*map(str, load_unknown_pool(raw)), *map(str, pool)})
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "unknown_pool.txt").write_text("\n".join(merged), encoding="utf-8")


def run_disease_sources(wanted: set[str], raw: Path, disease: Path, counts: Counter, unknown_pool: list[Path]) -> None:
    if "plantvillage" in wanted:
        repo = fetch_git(PLANTVILLAGE_SRC, raw / "PlantVillage-Dataset", sparse="raw/color")
        prepare_plantvillage(require_dir(repo / "raw" / "color", "PlantVillage raw/color"), disease, counts, unknown_pool)
    if "plantdoc" in wanted:
        repo = fetch_git(PLANTDOC_SRC, raw / "PlantDoc-Dataset")
        require_dir(repo / "train", "PlantDoc train/")
        prepare_plantdoc(repo, disease, counts, unknown_pool)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    parser.add_argument("--only", default=",".join(ALL_SOURCES), help=f"Comma list of: {', '.join(ALL_SOURCES)}")
    parser.add_argument("--max-per-crop", type=int, default=1500, help="Crop-ID images per crop / unknown.")
    parser.add_argument("--negatives-per-set", type=int, default=800)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    wanted = set(args.only.split(","))
    unknown_sources = wanted - set(ALL_SOURCES)
    if unknown_sources:
        raise SystemExit(f"Unknown source(s) {sorted(unknown_sources)}. Valid: {', '.join(ALL_SOURCES)}")
    random.seed(args.seed)
    raw, disease = args.out_dir / "raw", args.out_dir / "disease"
    counts: Counter = Counter()
    unknown_pool: list[Path] = []

    run_disease_sources(wanted, raw, disease, counts, unknown_pool)
    if "negatives" in wanted:
        unknown_pool.extend(fetch_negatives(raw / "negatives", args.negatives_per_set))
    save_unknown_pool(raw, unknown_pool)
    if "crop_id" in wanted:
        pool = load_unknown_pool(raw)
        build_crop_id(disease, pool, args.out_dir / "crop_id", args.max_per_crop, args.seed)
    print_report(disease)
    print(f"\nCrop-ID classes expected: {list(CROP_ID_SPEC.classes)}")


if __name__ == "__main__":
    main()
