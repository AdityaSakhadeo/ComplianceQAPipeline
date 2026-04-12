from __future__ import annotations

import os
from typing import Any

from ekip.retrieval.store import VectorStore


def _build_where_filter(
    doctype: str | None,
    department: str | None,
    created_year: str | None,
) -> dict[str, Any] | None:
    clauses: list[dict[str, Any]] = []
    if doctype:
        clauses.append({"doctype": doctype})
    if department:
        clauses.append({"department": department})
    if created_year:
        clauses.append({"created_year": created_year})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def retrieve_for_query(
    store: VectorStore,
    question: str,
    top_k: int = 5,
    doctype: str | None = None,
    department: str | None = None,
    created_year: str | None = None,
) -> list[dict[str, Any]]:
    """Metadata-aware retrieval; returns list of {text, metadata, distance}."""
    where = _build_where_filter(doctype, department, created_year)
    raw = store.query(question, n_results=top_k, where=where)
    docs = (raw.get("documents") or [[]])[0]
    metas = (raw.get("metadatas") or [[]])[0]
    dists = (raw.get("distances") or [[]])[0]
    out: list[dict[str, Any]] = []
    for i, text in enumerate(docs):
        out.append(
            {
                "text": text,
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else None,
            }
        )
    return out


def format_citations(hits: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, h in enumerate(hits, start=1):
        m = h.get("metadata") or {}
        src = m.get("source_file", "?")
        p0 = m.get("page_start", "?")
        p1 = m.get("page_end", p0)
        dt = m.get("doctype") or ""
        yr = m.get("created_year") or ""
        bits = []
        if dt:
            bits.append(f"type={dt}")
        if yr:
            bits.append(f"year={yr}")
        extra = ", ".join(bits)
        cite = f"[{i}] {src} (pages {p0}-{p1})"
        if extra:
            cite += f" — {extra}"
        lines.append(cite)
    return "\n".join(lines)


def _llm_messages(question: str, context_blocks: list[str], citations_block: str) -> tuple[str, str]:
    ctx = "\n\n---\n\n".join(context_blocks)
    system = (
        "You are an enterprise knowledge assistant. Answer only using the provided context. "
        "If the answer is not in the context, say you do not have enough information. "
        "After your answer, list the bracket citation numbers you relied on (e.g. [1], [2])."
    )
    user = f"Context:\n{ctx}\n\nCitation index:\n{citations_block}\n\nQuestion: {question}"
    return system, user


def _synthesize_with_llm(question: str, context_blocks: list[str], citations_block: str) -> str | None:
    """
    Prefer Azure OpenAI when endpoint + key + deployment are set; else OpenAI.com API key.
    """
    try:
        from openai import AzureOpenAI, OpenAI
    except ImportError:
        return None

    system, user = _llm_messages(question, context_blocks, citations_block)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    azure_endpoint = (os.environ.get("AZURE_OPENAI_ENDPOINT") or "").strip().rstrip("/")
    azure_key = (os.environ.get("AZURE_OPENAI_API_KEY") or "").strip()
    azure_deployment = (os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT") or "").strip()

    if azure_endpoint and azure_key and azure_deployment:
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        client = AzureOpenAI(
            api_key=azure_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        resp = client.chat.completions.create(
            model=azure_deployment,
            messages=messages,
            temperature=1,
        )
        choice = resp.choices[0].message.content
        return choice.strip() if choice else None

    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not key:
        return None

    client = OpenAI(api_key=key)
    model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
    )
    choice = resp.choices[0].message.content
    return choice.strip() if choice else None


def answer_query(
    store: VectorStore,
    question: str,
    top_k: int = 5,
    doctype: str | None = None,
    department: str | None = None,
    created_year: str | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Full RAG answer: retrieval + citation list + optional LLM synthesis.
    Without Azure OpenAI or OPENAI_API_KEY, returns extractive-style answer from top chunk snippets.
    """
    hits = retrieve_for_query(
        store,
        question,
        top_k=top_k,
        doctype=doctype,
        department=department,
        created_year=created_year,
    )
    citations = format_citations(hits)
    blocks = [h["text"] for h in hits]

    answer: str | None = None
    if use_llm:
        answer = _synthesize_with_llm(question, blocks, citations)

    if not answer:
        # Extractive fallback: quote first hits with pointers
        parts = [
            "No LLM configured (Azure OpenAI env vars or OPENAI_API_KEY) or synthesis failed. "
            "Relevant excerpts with citation indices:"
        ]
        for i, h in enumerate(hits, start=1):
            snippet = h["text"][:800] + ("…" if len(h["text"]) > 800 else "")
            parts.append(f"\n[{i}] {snippet}")
        answer = "\n".join(parts)

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "hits": hits,
    }
