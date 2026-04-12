# Streamlit RAG UI

Same retrieval and answering logic as `api/app.py` (FastAPI), in a browser UI.

## Local

```powershell
cd enterprise-rag-platform
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`). You need a populated **`data/vectorstore`** (and optionally `OPENAI_API_KEY` / Azure OpenAI for LLM answers).

## [Streamlit Community Cloud](https://streamlit.io/cloud)

1. Push this repo to GitHub (secrets stay in the Cloud UI, not in code).
2. **New app** → select repo, **Main file path**: `enterprise-rag-platform/streamlit_app.py`, **App URL** root: set to the **`ComplianceQAPipeline`** repo root if the UI asks for a directory, or point the app at the subfolder per Streamlit’s monorepo docs.
3. Under **Secrets**, add at least:
   ```toml
   OPENAI_API_KEY = "..."
   ```
   (or your Azure OpenAI variables as `st.secrets` keys matching what `python-dotenv` would load — for Cloud, prefer reading `st.secrets` in `streamlit_app.py` if you add that wiring.)
4. **Large caveat:** Community Cloud has **limited disk** and **no persistent** `data/vectorstore` unless you bake a small index into the repo or download at startup from object storage. For a full corpus, run Streamlit on a VM, Render, or similar with a volume.

## Portfolio site (`docs/`)

Set **`streamlitRagUrl`** in `docs/js/config.js` to your public Streamlit app URL so the GitHub Pages “Open Streamlit RAG” button works.

Optional **REST** path: deploy `uvicorn api.app:app` elsewhere and set **`ragApiBaseUrl`** for the embedded API form.
