from __future__ import annotations

import csv
from pathlib import Path

from ekip.config import DOCUMENT_METADATA_CSV


def infer_doctype_from_filename(name: str) -> str:
    n = name.lower()
    if "annual-report" in n:
        return "annual-report"
    if "csr-impact-assessment" in n:
        return "csr-impact-assessment"
    if "csr-policy" in n:
        return "csr-policy"
    if "codeofconduct" in n or "code-of-conduct" in n:
        return "code-of-conduct"
    if "human-rights" in n or "humanrights" in n:
        return "human-rights-statement"
    if "whistleblower" in n:
        return "whistleblower-policy"
    return ""


def load_document_metadata_table(path: Path | None = None) -> dict[str, dict[str, str]]:
    """
    Load filename -> {doctype, department, created_year} from TSV/CSV.
    Supports legacy column name 'dipartment'.
    """
    path = path or DOCUMENT_METADATA_CSV
    if not path.is_file():
        return {}

    rows: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        except csv.Error:
            dialect = csv.excel_tab

        reader = csv.DictReader(f, dialect=dialect)
        if not reader.fieldnames:
            return rows

        fn_key = "filename"
        dept_keys = ("department", "dipartment")
        dept_field = next((k for k in dept_keys if k in reader.fieldnames), None)

        for row in reader:
            fn = (row.get(fn_key) or "").strip()
            if not fn:
                continue
            dept = ""
            if dept_field:
                dept = (row.get(dept_field) or "").strip()
            rows[fn] = {
                "doctype": (row.get("doctype") or "").strip(),
                "department": dept,
                "created_year": (row.get("created_year") or "").strip(),
            }
    return rows
