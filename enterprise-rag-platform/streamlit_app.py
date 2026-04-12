"""
Streamlit UI for EKIP metadata-aware RAG (same logic as api.app FastAPI).

  cd enterprise-rag-platform
  streamlit run streamlit_app.py

Requires indexed Chroma data under data/vectorstore (run: python -m ekip index).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from ekip.config import COLLECTION_NAME, VECTOR_DIR
from ekip.rag.query import answer_query
from ekip.retrieval.store import VectorStore

st.set_page_config(page_title="EKIP RAG", layout="wide")

st.title("Enterprise Knowledge Intelligence Platform")
st.caption("Python · RAG · Chroma · metadata filters · LLM synthesis")


@st.cache_resource
def _vector_store() -> VectorStore:
    return VectorStore(persist_dir=VECTOR_DIR, collection_name=COLLECTION_NAME)


with st.sidebar:
    st.subheader("Retrieval filters")
    doctype = st.text_input("Document type", placeholder="e.g. annual-report", key="f_doctype")
    department = st.text_input("Department", placeholder="optional", key="f_dept")
    year = st.text_input("Created year", placeholder="e.g. 2003", key="f_year")
    top_k = st.slider("Top K chunks", min_value=1, max_value=20, value=5)
    use_llm = st.checkbox("LLM synthesis", value=True, help="Uses OPENAI_API_KEY or Azure OpenAI env vars when set.")

st.markdown(
    "Ask a question over your **indexed** corpus. "
    "Ensure `data/vectorstore` exists (`python -m ekip ingest` then `python -m ekip index`)."
)

question = st.text_area(
    "Your question",
    height=140,
    placeholder="e.g. What was the operating result in the first reporting period?",
)

col1, col2 = st.columns([1, 4])
with col1:
    run = st.button("Ask", type="primary", use_container_width=True)

if run:
    q = (question or "").strip()
    if not q:
        st.warning("Enter a question.")
    else:
        with st.spinner("Retrieving and synthesizing…"):
            try:
                store = _vector_store()
                out = answer_query(
                    store,
                    q,
                    top_k=top_k,
                    doctype=doctype.strip() or None,
                    department=department.strip() or None,
                    created_year=year.strip() or None,
                    use_llm=use_llm,
                )
                st.markdown("### Answer")
                st.markdown(out.get("answer") or "")
                st.markdown("### Citations")
                st.code(out.get("citations") or "", language=None)
            except Exception as e:
                st.error(f"Query failed: {e}")
