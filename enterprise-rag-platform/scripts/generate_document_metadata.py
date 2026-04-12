import os
import re
import csv
from pathlib import Path
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "raw" / "pdfs"
OUT_CSV = ROOT / "configs" / "document_metadata.csv"

def infer_doctype(name: str) -> str:
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

def parse_creation_year_from_meta(meta) -> str:
    if not meta:
        return ''
    # PyPDF2 may return attributes like '/CreationDate' or 'creation_date'
    for key in ('/CreationDate', 'CreationDate', 'creation_date', 'Created'):
        val = meta.get(key) if isinstance(meta, dict) else getattr(meta, key, None)
        if not val:
            continue
        s = str(val)
        m = re.search(r'20\d{2}', s)
        if m:
            return m.group(0)
    return ''

def parse_year_from_filename(name: str) -> str:
    m = re.search(r'20\d{2}', name)
    return m.group(0) if m else ''

def main():
    if PdfReader is None:
        print('pypdf not installed. Install requirements.txt and retry.')
        return

    rows = []
    for entry in sorted(PDF_DIR.iterdir()):
        if not entry.is_file() or entry.suffix.lower() != '.pdf':
            continue
        filename = entry.name
        doctype = infer_doctype(filename)
        department = ''
        created_year = ''
        try:
            reader = PdfReader(str(entry))
            meta = reader.metadata
            created_year = parse_creation_year_from_meta(meta) or parse_year_from_filename(filename)
        except Exception:
            created_year = parse_year_from_filename(filename)

        rows.append({
            'filename': filename,
            'doctype': doctype,
            'department': department,
            'created_year': created_year,
        })

    # Write TSV-like CSV to match existing file style (tab-separated)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','doctype','department','created_year'], delimiter='\t')
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f'Wrote {OUT_CSV} with {len(rows)} entries')

if __name__ == '__main__':
    main()
