from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ekip.config import CHUNKS_JSONL, DOCUMENT_METADATA_CSV, PROCESSED_DIR, RAW_PDF_DIR
from ekip.ingestion.chunking import chunk_page_text
from ekip.ingestion.extract import extract_pdf_pages
from ekip.ingestion.metadata import infer_doctype_from_filename, load_document_metadata_table
from ekip.ingestion.validate import is_valid_chunk


def _stable_chunk_id(source_file: str, page_start: int, page_end: int, chunk_index: int) -> str:
    raw = f"{source_file}|{page_start}|{page_end}|{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def run_ingestion(
    pdf_dir: Path | None = None,
    metadata_csv: Path | None = None,
    out_jsonl: Path | None = None,
) -> int:
    """
    Extract text from PDFs, validate chunks, merge CSV metadata, write JSONL.
    Returns number of chunks written.
    """
    pdf_dir = pdf_dir or RAW_PDF_DIR
    out_jsonl = out_jsonl or CHUNKS_JSONL
    meta_map = load_document_metadata_table(metadata_csv or DOCUMENT_METADATA_CSV)

    if not pdf_dir.is_dir():
        pdf_dir.mkdir(parents=True, exist_ok=True)

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with out_jsonl.open("w", encoding="utf-8") as out_f:
        for entry in sorted(pdf_dir.iterdir()):
            if not entry.is_file() or entry.suffix.lower() != ".pdf":
                continue

            filename = entry.name
            doc_meta = dict(meta_map.get(filename, {}))
            if not doc_meta.get("doctype"):
                doc_meta["doctype"] = infer_doctype_from_filename(filename)
            pages = extract_pdf_pages(entry)

            global_chunk_idx = 0
            for page_num, page_text in pages:
                for ps, pe, idx_on_page, chunk_text in chunk_page_text(page_num, page_text):
                    if not is_valid_chunk(chunk_text):
                        continue
                    cid = _stable_chunk_id(filename, ps, pe, global_chunk_idx)
                    record = {
                        "id": cid,
                        "text": chunk_text,
                        "metadata": {
                            "source_file": filename,
                            "page_start": ps,
                            "page_end": pe,
                            "chunk_index": global_chunk_idx,
                            "chunk_index_on_page": idx_on_page,
                            "doctype": doc_meta.get("doctype", ""),
                            "department": doc_meta.get("department", ""),
                            "created_year": doc_meta.get("created_year", ""),
                        },
                    }
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    global_chunk_idx += 1
                    count += 1

    return count
