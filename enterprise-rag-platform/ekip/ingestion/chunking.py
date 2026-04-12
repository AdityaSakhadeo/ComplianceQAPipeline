from __future__ import annotations

from ekip.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_page_text(page_num: int, text: str) -> list[tuple[int, int, int, str]]:
    """
    Split page text into overlapping chunks.
    Returns list of (page_start, page_end, chunk_index_on_page, chunk_text).
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= CHUNK_SIZE:
        return [(page_num, page_num, 0, text)]

    chunks: list[tuple[int, int, int, str]] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append((page_num, page_num, idx, piece))
            idx += 1
        if end >= len(text):
            break
        start = end - CHUNK_OVERLAP
        if start < 0:
            start = 0
    return chunks
