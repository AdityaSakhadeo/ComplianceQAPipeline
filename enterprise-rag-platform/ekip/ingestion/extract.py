from __future__ import annotations

from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore[misc, assignment]


def extract_pdf_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (1-based page number, text) for each page."""
    if PdfReader is None:
        raise RuntimeError("pypdf is required for PDF extraction. Install requirements.txt.")

    reader = PdfReader(str(pdf_path))
    out: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = text.strip()
        if text:
            out.append((i, text))
    return out
