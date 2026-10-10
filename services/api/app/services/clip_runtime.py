"""ONNX Runtime wrapper for pretrained CLIP: image/text embeddings and zero-shot scoring."""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.core.general_catalog import CLIP_SPEC, ClipSpec
from app.services.clip_tokenizer import ClipTokenizer
from app.services.onnx_model import ModelRuntimeError

PromptGroups = dict[str, tuple[str, ...]]


def _unit(vectors: np.ndarray) -> np.ndarray:
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)


class ClipEncoder:
    """Lazily loads the CLIP vision and text towers (from disk, no network) and scores prompts."""

    def __init__(self, spec: ClipSpec = CLIP_SPEC, models_dir: str | None = None) -> None:
        self._spec = spec
        self._models_dir = models_dir
        self._vision = None
        self._text = None
        self._tokenizer: ClipTokenizer | None = None
        self._text_cache: dict[tuple[str, ...], np.ndarray] = {}
        self._last_image: tuple[bytes, np.ndarray] | None = None

    def _folder(self) -> Path:
        return Path(self._models_dir or settings.AI_MODEL_PATH) / self._spec.folder

    def is_installed(self) -> bool:
        spec, folder = self._spec, self._folder()
        names = (spec.vision_file, spec.text_file, spec.vocab_file, spec.merges_file)
        return all((folder / name).exists() for name in names)

    def version(self) -> str:
        try:
            meta = json.loads((self._folder() / self._spec.meta_file).read_text(encoding="utf-8"))
            return str(meta["version"])
        except (OSError, ValueError, KeyError):
            return "unknown"

    def _load(self) -> None:
        if self._vision is not None:
            return
        try:
            import onnxruntime as ort

            folder, spec = self._folder(), self._spec
            options = ["CPUExecutionProvider"]
            self._vision = ort.InferenceSession(str(folder / spec.vision_file), providers=options)
            self._text = ort.InferenceSession(str(folder / spec.text_file), providers=options)
            self._tokenizer = ClipTokenizer(folder / spec.vocab_file, folder / spec.merges_file)
        except Exception as exc:
            self._vision = None
            raise ModelRuntimeError(f"Could not load the general CLIP model: {exc}") from exc

    def _preprocess(self, bgr: np.ndarray) -> np.ndarray:
        size = self._spec.input_size
        pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        scale = size / min(pil.size)
        resized = pil.resize(
            (max(size, round(pil.width * scale)), max(size, round(pil.height * scale))),
            Image.Resampling.BICUBIC,
        )
        left, top = (resized.width - size) // 2, (resized.height - size) // 2
        crop = np.asarray(resized.crop((left, top, left + size, top + size)), np.float32) / 255.0
        crop = (crop - np.array(self._spec.mean, np.float32)) / np.array(self._spec.std, np.float32)
        return crop.transpose(2, 0, 1)[None, ...]

    def encode_image(self, bgr: np.ndarray) -> np.ndarray:
        """Unit-length image embedding; the most recent image is cached (crop ID + category share it)."""
        key = hashlib.blake2b(bgr.tobytes(), digest_size=16).digest()
        if self._last_image and self._last_image[0] == key:
            return self._last_image[1]
        self._load()
        out = self._vision.run(None, {"pixel_values": self._preprocess(bgr)})[0]
        embedding = _unit(out)[0]
        self._last_image = (key, embedding)
        return embedding

    def encode_texts(self, prompts: tuple[str, ...]) -> np.ndarray:
        """Unit-length text embeddings, cached per prompt tuple."""
        if prompts in self._text_cache:
            return self._text_cache[prompts]
        self._load()
        token_lists = [self._tokenizer.encode(p) for p in prompts]
        width = max(map(len, token_lists))
        ids = np.array(
            [t + [self._tokenizer.end_id] * (width - len(t)) for t in token_lists], dtype=np.int64
        )
        embeddings = _unit(self._text.run(None, {"input_ids": ids})[0])
        self._text_cache[prompts] = embeddings
        return embeddings

    def group_probabilities(self, bgr: np.ndarray, groups: PromptGroups) -> list[tuple[str, float]]:
        """Softmax over one averaged text embedding per prompt group; best first.

        Averaging prompts per group (not summing per-prompt probabilities) keeps groups with many
        prompts from outweighing groups with few. Scores are relative to the offered groups only
        and are NOT calibrated probabilities.
        """
        centroids = np.stack([_unit(self.encode_texts(group).mean(axis=0)) for group in groups.values()])
        logits = self._spec.logit_scale * (centroids @ self.encode_image(bgr))
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        return sorted(zip(groups, map(float, probs), strict=True), key=lambda item: -item[1])


clip_encoder = ClipEncoder()
