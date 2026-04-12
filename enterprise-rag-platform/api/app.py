"""
FastAPI service for metadata-aware RAG queries.
Run from repo root of enterprise-rag-platform:

  uvicorn api.app:app --host 0.0.0.0 --port 8088

Set CORS_ORIGINS to a comma-separated list, or leave unset for permissive demo defaults.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from ekip.config import COLLECTION_NAME, VECTOR_DIR
from ekip.rag.query import answer_query
from ekip.retrieval.store import VectorStore

app = FastAPI(title="EKIP RAG API", version="0.1.0")

_origins_env = (os.environ.get("CORS_ORIGINS") or "").strip()
if _origins_env:
    _cors_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    _cors_origins = [
        "https://adityasakhadeo.github.io",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(persist_dir=VECTOR_DIR, collection_name=COLLECTION_NAME)
    return _store


class QueryBody(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(5, ge=1, le=20)
    doctype: str | None = None
    department: str | None = None
    year: str | None = None
    use_llm: bool = True


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/rag/query")
def rag_query(body: QueryBody) -> dict:
    q = body.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="question required")
    try:
        store = get_store()
        return answer_query(
            store,
            q,
            top_k=body.top_k,
            doctype=body.doctype,
            department=body.department,
            created_year=body.year,
            use_llm=body.use_llm,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
