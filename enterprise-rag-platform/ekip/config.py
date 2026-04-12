from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_PDF_DIR = DATA_DIR / "raw" / "pdfs"
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"
VECTOR_DIR = DATA_DIR / "vectorstore"
CONFIG_DIR = ROOT / "configs"
DOCUMENT_METADATA_CSV = CONFIG_DIR / "document_metadata.csv"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 40
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "enterprise_docs"
