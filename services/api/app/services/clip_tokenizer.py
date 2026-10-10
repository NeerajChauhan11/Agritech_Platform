"""Minimal CLIP byte-pair-encoding tokenizer (vocab.json + merges.txt, lower-cased text)."""

import json
import re
from functools import lru_cache
from pathlib import Path

START_TOKEN = "<|startoftext|>"
END_TOKEN = "<|endoftext|>"
MAX_TOKENS = 77
# ASCII-oriented approximation of CLIP's pattern; prompts here are plain English.
_PATTERN = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d|[^\W\d_]+|\d|[^\s\w]+", re.IGNORECASE)


@lru_cache(maxsize=1)
def _byte_to_unicode() -> dict[int, str]:
    keep = [*range(33, 127), *range(161, 173), *range(174, 256)]
    chars = list(keep)
    extra = 0
    for byte in range(256):
        if byte not in keep:
            keep.append(byte)
            chars.append(256 + extra)
            extra += 1
    return dict(zip(keep, map(chr, chars), strict=True))


class ClipTokenizer:
    """Turns text into CLIP token ids: <start> + BPE tokens + <end>."""

    def __init__(self, vocab_file: Path, merges_file: Path) -> None:
        self._vocab: dict[str, int] = json.loads(vocab_file.read_text(encoding="utf-8"))
        lines = merges_file.read_text(encoding="utf-8").splitlines()[1:]
        self._ranks = {tuple(line.split()): rank for rank, line in enumerate(lines) if line.strip()}
        self._cache: dict[str, list[str]] = {}
        self.end_id = self._vocab[END_TOKEN]

    def _bpe(self, token: str) -> list[str]:
        if token in self._cache:
            return self._cache[token]
        parts = [*token[:-1], token[-1] + "</w>"]
        while len(parts) > 1:
            pairs = {(parts[i], parts[i + 1]) for i in range(len(parts) - 1)}
            best = min(pairs, key=lambda pair: self._ranks.get(pair, float("inf")))
            if best not in self._ranks:
                break
            merged: list[str] = []
            i = 0
            while i < len(parts):
                if i < len(parts) - 1 and (parts[i], parts[i + 1]) == best:
                    merged.append(parts[i] + parts[i + 1])
                    i += 2
                else:
                    merged.append(parts[i])
                    i += 1
            parts = merged
        self._cache[token] = parts
        return parts

    def encode(self, text: str) -> list[int]:
        """Token ids for one string, truncated to the 77-token CLIP context."""
        table = _byte_to_unicode()
        ids = [self._vocab[START_TOKEN]]
        for word in _PATTERN.findall(" ".join(text.lower().split())):
            mapped = "".join(table[b] for b in word.encode("utf-8"))
            ids.extend(self._vocab[piece] for piece in self._bpe(mapped))
        return [*ids[: MAX_TOKENS - 1], self.end_id]
