"""Download the pretrained CLIP weights used by the general-category diagnosis tier.

Run once while online so the demo works fully offline afterwards:

    python scripts/fetch_general_model.py [--models-dir services/api/models]

Source: OpenAI CLIP ViT-B/16 (MIT licence), ONNX export by Xenova on Hugging Face,
pinned to one commit. Every file is verified against a pinned SHA-256; nothing is
substituted if a download or checksum fails. Writes `clip_general/meta.json`.
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "Xenova/clip-vit-base-patch16"
REVISION = "342fdf2f67aded64d138ff074745fb4a5d2bba5f"
BASE_MODEL = "openai/clip-vit-base-patch16"
VERSION = "clip-vit-b16-zeroshot-1"
SUBDIR = "clip_general"
URL = "https://huggingface.co/{repo}/resolve/{rev}/{path}"

# local name -> (path in repo, pinned sha256)
FILES: dict[str, tuple[str, str]] = {
    "vision_model.onnx": (
        "onnx/vision_model.onnx",
        "b5170b47c0ecc667c9af5b42ed460c341377706d1466d177798c65fe49ea1e6b",
    ),
    "text_model.onnx": (
        "onnx/text_model.onnx",
        "19f40c7988af119fc50dabfe8015da8595c0372000e2c1f1a6289e35930577aa",
    ),
    "vocab.json": ("vocab.json", "5047b556ce86ccaf6aa22b3ffccfc52d391ea4accdab9c2f2407da5b742d4363"),
    "merges.txt": ("merges.txt", "9fd691f7c8039210e0fced15865466c65820d09b63988b0174bfe25de299051a"),
}
CHUNK = 1 << 20


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, target: Path) -> None:
    part = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url, timeout=60) as response, part.open("wb") as out:  # noqa: S310
        while block := response.read(CHUNK):
            out.write(block)
    part.replace(target)


def fetch_file(name: str, repo_path: str, expected: str, folder: Path) -> str:
    target = folder / name
    if target.exists() and sha256_of(target) == expected:
        print(f"ok (cached)  {name}")
        return expected
    print(f"downloading  {name} ...")
    download(URL.format(repo=REPO, rev=REVISION, path=repo_path), target)
    actual = sha256_of(target)
    if actual != expected:
        target.unlink(missing_ok=True)
        raise SystemExit(f"CHECKSUM MISMATCH for {name}: expected {expected}, got {actual}. Removed.")
    print(f"ok           {name}")
    return actual


def main() -> None:
    default_dir = Path(__file__).resolve().parents[1] / "services" / "api" / "models"
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models-dir", type=Path, default=default_dir)
    folder = parser.parse_args().models_dir / SUBDIR
    folder.mkdir(parents=True, exist_ok=True)

    checksums = {name: fetch_file(name, path, sha, folder) for name, (path, sha) in FILES.items()}
    meta = {
        "version": VERSION,
        "source": f"https://huggingface.co/{REPO}",
        "revision": REVISION,
        "base_model": BASE_MODEL,
        "license": "MIT (OpenAI CLIP)",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": checksums,
    }
    (folder / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Done. Weights and meta.json are in {folder}")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        sys.exit(f"Download failed ({exc}). Place the files listed in FILES into the models folder manually.")
