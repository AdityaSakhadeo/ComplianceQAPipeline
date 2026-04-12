from __future__ import annotations

from ekip.config import MIN_CHUNK_CHARS


def is_valid_chunk(text: str) -> bool:
    t = text.strip()
    if len(t) < MIN_CHUNK_CHARS:
        return False
    # Drop chunks that are mostly non-alphanumeric (likely garbled extraction)
    letters = sum(1 for c in t if c.isalnum())
    if letters < len(t) * 0.15 and len(t) < 200:
        return False
    return True
