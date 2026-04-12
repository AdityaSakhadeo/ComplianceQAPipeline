# Site (`docs/`)

Portfolio UI for **EKIP RAG** (Streamlit + optional REST) and **Compliance QA**.

Configure **`js/config.js`**:

- **`streamlitRagUrl`** — public Streamlit app (primary RAG demo button).
- **`ragApiBaseUrl`** — optional FastAPI for the in-page REST form under “Optional: ask via REST API”.
- **`apiBaseUrl`** — compliance audit API.

## Host this folder

Repository **Settings → Pages** → branch **`main`** / **`master`**, folder **`/docs`**.

## Assets

- `assets/ekip-architecture.png` — RAG diagram (see also `../enterprise-rag-platform/ekip-architecture.png`).
- `assets/pipeline-architecture.png` — compliance pipeline.

## RAG

- **Streamlit:** `../enterprise-rag-platform/STREAMLIT.md`
- **REST / Docker / hosts:** `../enterprise-rag-platform/DEPLOY-FREE.md`

Enable **CORS** on any REST API for your Pages origin.
