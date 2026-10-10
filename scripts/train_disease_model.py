#!/usr/bin/env python
"""Fine-tune a MobileNetV3 classifier and export it as ONNX for the AgriSmart API.

Two modes (class lists come from services/api/app/core/model_catalog.py, so the
trained model always matches what the API expects):

  disease  one model per crop      -> <out>/disease_<crop>.onnx
  crop-id  crop identifier + unknown -> <out>/crop_id.onnx

Data layout: one folder per class (images may be nested). PlantVillage folder
names ("Tomato___Early_blight") are understood; use --alias for other names.

Outputs next to the weights: <name>.meta.json (version, classes, preprocessing)
and <name>.metrics.json (held-out accuracy, per-class F1, confusion matrix).

Examples:
  python scripts/train_disease_model.py --mode disease --crop tomato --data-dir data/plantvillage
  python scripts/train_disease_model.py --mode crop-id --data-dir data/crop_id
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "services" / "api"))

from app.core.constants import CROP_ALIASES, SUPPORTED_CROPS
from app.core.crops import normalize_crop

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
# PlantVillage folder names that differ from the catalog class names.
BUILTIN_ALIASES = {
    "spider_mites_two_spotted_spider_mite": "spider_mites",
    "tomato_yellow_leaf_curl_virus": "yellow_leaf_curl_virus",
    "tomato_mosaic_virus": "mosaic_virus",
}
VAL_CAVEAT = (
    "Validation images come from the same dataset as training. Lab-style datasets such as "
    "PlantVillage generalise poorly to field photos: expect lower real-world accuracy."
)


def normalize(name: str) -> str:
    """'Tomato___Early blight' -> 'early_blight'."""
    if "___" in name:
        name = name.split("___", 1)[1]
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def crop_prefix_matches(folder: str, crop: str | None) -> bool:
    """PlantVillage root holds every crop; keep only folders for `crop` (or one of its aliases,
    e.g. PlantVillage's "Pepper,_bell" folders belong to the canonical `capsicum`)."""
    if crop is None or "___" not in folder:
        return True
    names = (crop, *(alias for alias, canonical in CROP_ALIASES.items() if canonical == crop))
    return re.sub(r"[^a-z0-9]+", "_", folder.split("___", 1)[0].lower()).startswith(names)


def stratified_split(labels: list[int], val_fraction: float, seed: int) -> tuple[list[int], list[int]]:
    """Split sample indices so every class appears in both train and validation."""
    rng = random.Random(seed)
    by_class: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        by_class.setdefault(label, []).append(idx)
    train, val = [], []
    for label, indices in sorted(by_class.items()):
        if len(indices) < 2:
            raise ValueError(f"Class index {label} has fewer than 2 images; cannot hold out validation data.")
        rng.shuffle(indices)
        n_val = min(len(indices) - 1, max(1, round(len(indices) * val_fraction)))
        val.extend(indices[:n_val])
        train.extend(indices[n_val:])
    return train, val


def compute_metrics(y_true: list[int], y_pred: list[int], classes: list[str]) -> dict:
    """Accuracy, per-class precision/recall/F1 and the confusion matrix (rows = truth)."""
    n = len(classes)
    matrix = [[0] * n for _ in range(n)]
    for truth, pred in zip(y_true, y_pred, strict=True):
        matrix[truth][pred] += 1
    per_class, f1s = {}, []
    for i, name in enumerate(classes):
        tp = matrix[i][i]
        support = sum(matrix[i])
        predicted = sum(row[i] for row in matrix)
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[name] = {"precision": round(precision, 4), "recall": round(recall, 4),
                           "f1": round(f1, 4), "support": support}
        f1s.append(f1)
    total = len(y_true)
    correct = sum(matrix[i][i] for i in range(n))
    return {
        "accuracy": round(correct / total, 4) if total else 0.0,
        "macro_f1": round(sum(f1s) / n, 4),
        "per_class": per_class,
        "confusion_matrix": {"labels": classes, "matrix": matrix},
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=["disease", "crop-id"], required=True)
    p.add_argument("--crop", help=f"Crop for disease mode: {', '.join(SUPPORTED_CROPS)}.")
    p.add_argument("--dataset-name", help="Name recorded in the model metadata (default: data-dir folder name).")
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=REPO_ROOT / "services" / "api" / "models")
    p.add_argument("--epochs", type=int, default=12, help="Full fine-tuning epochs.")
    p.add_argument("--head-epochs", type=int, default=2, help="Epochs training only the new head first.")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--val-fraction", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--version", help="Model version string (default: UTC timestamp).")
    p.add_argument("--no-pretrained", action="store_true", help="Do not download ImageNet weights.")
    p.add_argument("--alias", action="append", default=[], metavar="FOLDER=CLASS",
                   help="Map a normalised folder name to a catalog class (repeatable).")
    return p.parse_args(argv)


def resolve_spec(args: argparse.Namespace):
    from app.core.model_catalog import CROP_ID_SPEC, DISEASE_MODEL_SPECS

    if args.mode == "crop-id":
        return CROP_ID_SPEC
    crop = normalize_crop(args.crop)
    if crop is None:
        raise SystemExit(f"--crop must be one of: {', '.join(SUPPORTED_CROPS)} (got {args.crop!r})")
    args.crop = crop
    return DISEASE_MODEL_SPECS[crop]


def collect_samples(data_dir: Path, spec, crop: str | None, aliases: dict[str, str]):
    """Return (paths, labels) with labels indexing spec.classes; fail on any mismatch."""
    classes = list(spec.classes)
    paths: list[Path] = []
    labels: list[int] = []
    unmatched: list[str] = []
    found: set[str] = set()
    for folder in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        if not crop_prefix_matches(folder.name, crop):
            continue
        key = normalize(folder.name)
        key = aliases.get(key, key)
        if key not in classes:
            unmatched.append(folder.name)
            continue
        found.add(key)
        files = [f for f in folder.rglob("*") if f.suffix.lower() in IMAGE_SUFFIXES]
        paths += files
        labels += [classes.index(key)] * len(files)
    missing = [c for c in classes if c not in found]
    if missing or unmatched:
        raise SystemExit(
            f"Dataset does not match the catalog.\n  missing class folders: {missing}\n"
            f"  unrecognised folders: {unmatched}\n  (use --alias FOLDER=CLASS to map names)"
        )
    return paths, labels


class LeafDataset:
    """Map-style dataset (duck-typed for torch DataLoader)."""

    def __init__(self, paths: list[Path], labels: list[int], transform) -> None:
        self.paths, self.labels, self.transform = paths, labels, transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        from PIL import Image

        with Image.open(self.paths[index]) as img:
            return self.transform(img.convert("RGB")), self.labels[index]


def build_transforms(spec):
    from torchvision import transforms as T

    norm = T.Normalize(spec.mean, spec.std)
    size = spec.input_size
    train = T.Compose([
        T.RandomResizedCrop(size, scale=(0.6, 1.0)), T.RandomHorizontalFlip(), T.RandomVerticalFlip(),
        T.RandomRotation(25), T.ColorJitter(0.3, 0.3, 0.3, 0.05), T.ToTensor(), norm,
    ])
    val = T.Compose([T.Resize((size, size)), T.ToTensor(), norm])
    return train, val


def build_model(n_classes: int, pretrained: bool):
    import torch
    from torchvision import models

    weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
    model = models.mobilenet_v3_large(weights=weights)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, n_classes)
    return model


def run_epochs(model, loader, criterion, params, lr, epochs, device) -> None:
    import torch

    if epochs <= 0:
        return
    optimizer = torch.optim.AdamW(params, lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    for epoch in range(epochs):
        model.train()
        total = 0.0
        for images, targets in loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), targets)
            loss.backward()
            optimizer.step()
            total += float(loss) * len(targets)
        scheduler.step()
        print(f"  epoch {epoch + 1}/{epochs}  train_loss={total / len(loader.dataset):.4f}")


def predict_all(model, loader, device) -> tuple[list[int], list[int]]:
    import torch

    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for images, targets in loader:
            y_pred += model(images.to(device)).argmax(1).cpu().tolist()
            y_true += targets.tolist()
    return y_true, y_pred


def export_onnx(model, spec, path: Path) -> None:
    import torch

    model.cpu().eval()
    dummy = torch.randn(1, 3, spec.input_size, spec.input_size)
    kwargs = {
        "input_names": ["input"], "output_names": ["logits"], "opset_version": 17,
        "dynamic_axes": {"input": {0: "batch"}, "logits": {0: "batch"}},
    }
    try:
        torch.onnx.export(model, dummy, str(path), dynamo=False, **kwargs)
    except TypeError:  # older torch has no `dynamo` argument
        torch.onnx.export(model, dummy, str(path), **kwargs)
    verify_onnx(model, dummy, path)


def verify_onnx(model, dummy, path: Path) -> None:
    """Check the exported graph reproduces PyTorch outputs (skipped without onnxruntime)."""
    import torch

    try:
        import onnxruntime as ort
    except ImportError:
        print("  onnxruntime not installed: skipped ONNX output verification")
        return
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    onnx_out = session.run(None, {"input": dummy.numpy()})[0]
    with torch.no_grad():
        diff = float(abs(model(dummy).numpy() - onnx_out).max())
    if diff > 1e-3:
        raise SystemExit(f"ONNX output differs from PyTorch by {diff:.5f}; export is unreliable.")
    print(f"  ONNX verified against PyTorch (max diff {diff:.2e})")


def write_reports(args, spec, weights: Path, metrics: dict, counts: tuple[int, int]) -> None:
    version = args.version or datetime.now(timezone.utc).strftime("%Y.%m.%d-%H%M")
    meta = {
        "version": version, "key": spec.key, "classes": list(spec.classes),
        "input_size": spec.input_size, "mean": list(spec.mean), "std": list(spec.std),
        "architecture": spec.architecture, "dataset": str(args.data_dir),
        "dataset_name": args.dataset_name or args.data_dir.name,
        "seed": args.seed, "val_accuracy": metrics["accuracy"],
    }
    weights.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    report = {**metrics, "train_images": counts[0], "val_images": counts[1], "caveat": VAL_CAVEAT}
    weights.with_suffix(".metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def make_loaders(args, spec, paths, labels, train_idx, val_idx):
    from torch.utils.data import DataLoader

    train_tf, val_tf = build_transforms(spec)

    def loader(indices, transform, shuffle):
        dataset = LeafDataset([paths[i] for i in indices], [labels[i] for i in indices], transform)
        return DataLoader(dataset, args.batch_size, shuffle=shuffle, num_workers=args.workers)

    return loader(train_idx, train_tf, True), loader(val_idx, val_tf, False)


def fit(args, spec, train_loader, train_labels, device):
    """Two-phase fine-tuning: new head on a frozen backbone, then the whole network."""
    import torch

    model = build_model(len(spec.classes), not args.no_pretrained).to(device)
    counts = torch.bincount(torch.tensor(train_labels), minlength=len(spec.classes)).float()
    weight = (counts.sum() / (len(counts) * counts.clamp(min=1))).to(device)
    criterion = torch.nn.CrossEntropyLoss(weight=weight, label_smoothing=0.05)
    for p in model.features.parameters():
        p.requires_grad = False
    run_epochs(model, train_loader, criterion, model.classifier.parameters(), 1e-3, args.head_epochs, device)
    for p in model.features.parameters():
        p.requires_grad = True
    run_epochs(model, train_loader, criterion, model.parameters(), args.lr, args.epochs, device)
    return model


def train(args: argparse.Namespace) -> None:
    import torch

    spec = resolve_spec(args)
    aliases = {**BUILTIN_ALIASES, **dict(a.split("=", 1) for a in args.alias)}
    paths, labels = collect_samples(args.data_dir, spec, args.crop, aliases)
    train_idx, val_idx = stratified_split(labels, args.val_fraction, args.seed)
    print(f"{spec.key}: {len(train_idx)} train / {len(val_idx)} validation images, {len(spec.classes)} classes")

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, val_loader = make_loaders(args, spec, paths, labels, train_idx, val_idx)
    model = fit(args, spec, train_loader, [labels[i] for i in train_idx], device)

    y_true, y_pred = predict_all(model, val_loader, device)
    metrics = compute_metrics(y_true, y_pred, list(spec.classes))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights = args.out_dir / spec.weights_file
    export_onnx(model, spec, weights)
    write_reports(args, spec, weights, metrics, (len(train_idx), len(val_idx)))
    print(f"held-out accuracy {metrics['accuracy']:.3f}, macro F1 {metrics['macro_f1']:.3f} -> {weights}")


if __name__ == "__main__":
    train(parse_args())
