from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ekip.config import CHUNKS_JSONL, COLLECTION_NAME, RAW_PDF_DIR, ROOT, VECTOR_DIR
from ekip.ingestion.pipeline import run_ingestion
from ekip.rag.query import answer_query
from ekip.retrieval.store import VectorStore


def _cmd_ingest(args: argparse.Namespace) -> int:
    n = run_ingestion(
        pdf_dir=Path(args.pdf_dir) if args.pdf_dir else None,
        metadata_csv=Path(args.metadata_csv) if args.metadata_csv else None,
        out_jsonl=Path(args.out_jsonl) if args.out_jsonl else None,
    )
    print(f"Ingestion complete: {n} chunks -> {args.out_jsonl or CHUNKS_JSONL}")
    return 0


def _cmd_index(args: argparse.Namespace) -> int:
    store = VectorStore(
        persist_dir=Path(args.vector_dir) if args.vector_dir else None,
        collection_name=args.collection,
    )
    n = store.index_jsonl(jsonl_path=Path(args.jsonl) if args.jsonl else None, reset=args.reset)
    print(f"Indexed {n} chunks into Chroma at {args.vector_dir or VECTOR_DIR}")
    return 0


def _cmd_query(args: argparse.Namespace) -> int:
    store = VectorStore(
        persist_dir=Path(args.vector_dir) if args.vector_dir else None,
        collection_name=args.collection,
    )
    result = answer_query(
        store,
        args.question,
        top_k=args.top_k,
        doctype=args.doctype or None,
        department=args.department or None,
        created_year=args.year or None,
        use_llm=not args.no_llm,
    )
    print(result["answer"])
    print("\n--- Citations ---\n")
    print(result["citations"])
    return 0


def main(argv: list[str] | None = None) -> int:
    # Load .env if present
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    p = argparse.ArgumentParser(
        prog="python -m ekip",
        description="Enterprise Knowledge Intelligence Platform (RAG MVP)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="Extract PDFs, validate, write JSONL chunks")
    pi.add_argument("--pdf-dir", default="", help="PDF directory (default: data/raw/pdfs)")
    pi.add_argument("--metadata-csv", default="", help="document_metadata.csv path")
    pi.add_argument("--out-jsonl", default="", help="Output JSONL path")
    pi.set_defaults(func=_cmd_ingest)

    px = sub.add_parser("index", help="Embed chunks and persist vector index")
    px.add_argument("--jsonl", default="", help="Chunks JSONL path")
    px.add_argument("--vector-dir", default="", help="Chroma persist directory")
    px.add_argument("--collection", default="", help="Collection name override")
    px.add_argument("--reset", action="store_true", help="Drop collection before re-indexing")
    px.set_defaults(func=_cmd_index)

    pq = sub.add_parser("query", help="Metadata-aware RAG query with citations")
    pq.add_argument("question", nargs="+", help="Natural language question")
    pq.add_argument("--top-k", type=int, default=5)
    pq.add_argument("--doctype", default="", help="Filter by document type")
    pq.add_argument("--department", default="", help="Filter by department")
    pq.add_argument("--year", default="", help="Filter by created_year metadata")
    pq.add_argument("--vector-dir", default="", help="Chroma persist directory")
    pq.add_argument("--collection", default="", help="Collection name")
    pq.add_argument("--no-llm", action="store_true", help="Skip OpenAI; extractive snippets only")
    pq.set_defaults(func=_cmd_query)

    args = p.parse_args(argv)
    # Fill defaults for optional path strings
    if hasattr(args, "pdf_dir") and not args.pdf_dir:
        args.pdf_dir = str(RAW_PDF_DIR)
    if hasattr(args, "out_jsonl") and not args.out_jsonl:
        args.out_jsonl = str(CHUNKS_JSONL)
    if hasattr(args, "jsonl") and not args.jsonl:
        args.jsonl = str(CHUNKS_JSONL)
    if hasattr(args, "vector_dir") and not args.vector_dir:
        args.vector_dir = str(VECTOR_DIR)

    if hasattr(args, "collection") and not args.collection:
        args.collection = COLLECTION_NAME

    if args.cmd == "query":
        args.question = " ".join(args.question)

    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
