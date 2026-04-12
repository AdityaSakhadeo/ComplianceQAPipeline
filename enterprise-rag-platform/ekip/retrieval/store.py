from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from ekip.config import CHUNKS_JSONL, COLLECTION_NAME, EMBEDDING_MODEL, VECTOR_DIR


def _chroma_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """Chroma accepts str, int, float, bool only."""
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


class VectorStore:
    def __init__(
        self,
        persist_dir: Path | None = None,
        collection_name: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir or VECTOR_DIR)
        self.collection_name = collection_name or COLLECTION_NAME
        self.model_name = model_name or EMBEDDING_MODEL
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.model_name
        )
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    def index_jsonl(self, jsonl_path: Path | None = None, reset: bool = False) -> int:
        """Load chunks from JSONL and upsert into Chroma. Returns number of vectors."""
        path = jsonl_path or CHUNKS_JSONL
        if not path.is_file():
            raise FileNotFoundError(f"Missing chunks file: {path}")

        if reset:
            try:
                self._client.delete_collection(self.collection_name)
            except Exception:
                pass
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self._ef,
                metadata={"hnsw:space": "cosine"},
            )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []

        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                cid = row["id"]
                text = row["text"]
                meta = _chroma_metadata(row.get("metadata") or {})
                ids.append(cid)
                documents.append(text)
                metadatas.append(meta)

        if not ids:
            return 0

        batch = 128
        for i in range(0, len(ids), batch):
            self._collection.upsert(
                ids=ids[i : i + batch],
                documents=documents[i : i + batch],
                metadatas=metadatas[i : i + batch],
            )
        return len(ids)

    def query(
        self,
        question: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "query_texts": [question],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        return self._collection.query(**kwargs)
