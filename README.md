# Compliance QA Pipeline

Azure multi-modal compliance orchestration: **Video Indexer** → transcript/OCR → **Azure AI Search** (RAG) → **Azure OpenAI** (LangGraph).

## Portfolio site (GitHub Pages)

Enable **Settings → Pages** with source **`/docs`**. Configure [`docs/js/config.js`](docs/js/config.js) (`streamlitRagUrl`, optional `ragApiBaseUrl`, `apiBaseUrl`). RAG: [`enterprise-rag-platform/STREAMLIT.md`](enterprise-rag-platform/STREAMLIT.md) · hosts: [`enterprise-rag-platform/DEPLOY-FREE.md`](enterprise-rag-platform/DEPLOY-FREE.md).

## Run locally

```bash
uv sync
python main.py
```

Use `.env` for Azure credentials (never commit secrets).
