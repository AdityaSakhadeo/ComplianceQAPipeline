# Compliance QA Pipeline

Azure multi-modal compliance orchestration: **Video Indexer** → transcript/OCR → **Azure AI Search** (RAG) → **Azure OpenAI** (LangGraph).

## Portfolio site (GitHub Pages)

Enable **Settings → Pages** with source **`/docs`**. The UI is in [`docs/`](docs/); set API base URLs in [`docs/js/config.js`](docs/js/config.js). RAG API deployment options: [`enterprise-rag-platform/DEPLOY-FREE.md`](enterprise-rag-platform/DEPLOY-FREE.md).

## Run locally

```bash
uv sync
python main.py
```

Use `.env` for Azure credentials (never commit secrets).
