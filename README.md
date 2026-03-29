# Compliance QA Pipeline

Azure multi-modal compliance orchestration: **Video Indexer** → transcript/OCR → **Azure AI Search** (RAG) → **Azure OpenAI** (LangGraph).

## Live demo (GitHub Pages)

Enable **Settings → Pages** with source **`/docs`**. The static UI lives in [`docs/`](docs/); configure a backend URL in [`docs/js/config.js`](docs/js/config.js) when you deploy an API.

## Run locally

```bash
uv sync
python main.py
```

Use `.env` for Azure credentials (never commit secrets).
