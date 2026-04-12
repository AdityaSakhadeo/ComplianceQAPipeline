# Deploy the RAG API (free / low-cost options)

The frontend calls **`POST /api/rag/query`** with JSON `{ "question": "..." }`. Your host must set **`CORS_ORIGINS`** to include your site origin (e.g. `https://yourname.github.io`).

## Option A — [Render](https://render.com) (free web service)

1. Push this repo (or only `enterprise-rag-platform`) to GitHub.
2. **New → Web Service**, connect the repo, root directory: **`enterprise-rag-platform`**.
3. **Runtime**: Docker (uses the `Dockerfile` here), or **Native**:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
4. **Environment** (minimum):
   - `CORS_ORIGINS` — your Pages URL, e.g. `https://yourname.github.io`
   - `OPENAI_API_KEY` or Azure OpenAI vars — for LLM answers (`answer_query` in code)
5. **Vector index**: the free tier has **ephemeral disk**. After each deploy you must either:
   - Run **ingest + index** once via a **Render shell** / one-off job, or  
   - Build a Docker image that **includes** `data/vectorstore` (run `python -m ekip index` locally, commit only if small enough, or use a volume on a paid tier).

## Option B — [Fly.io](https://fly.io) (free allowance)

1. Install `flyctl`, run `fly launch` in `enterprise-rag-platform` (use the Dockerfile).
2. Set secrets: `fly secrets set OPENAI_API_KEY=... CORS_ORIGINS=https://...`
3. Attach a **volume** for `data/vectorstore` if you want the index to survive restarts.

## Option C — [Koyeb](https://www.koyeb.com)

Similar to Render: GitHub repo, Dockerfile or buildpack, set `PORT` and env vars.

## Option D — [Streamlit](https://streamlit.io/) (recommended RAG UI)

Interactive app: **`streamlit_app.py`** (same `answer_query` logic as FastAPI).

- **Local:** `pip install -r requirements.txt` then `streamlit run streamlit_app.py`
- **Cloud:** [Streamlit Community Cloud](https://streamlit.io/cloud) — see **`STREAMLIT.md`**

Paste your public Streamlit URL into **`docs/js/config.js`** → **`streamlitRagUrl`** for the portfolio “Open Streamlit RAG” button.

**Optional REST API** (for the embedded form on Pages): still deploy `uvicorn api.app:app` and set **`ragApiBaseUrl`**.

## After deploy

1. For **Streamlit**, copy the app URL into **`docs/js/config.js`** → `streamlitRagUrl` (no trailing slash).
2. For **REST only**, set `ragApiBaseUrl` instead (or both).
3. Redeploy or refresh GitHub Pages.

**Note:** `sentence-transformers` + Chroma need **RAM**; free tiers may OOM on first embed. If that happens, use a host with **≥1 GB RAM** or switch embedding strategy in code for a lighter model.
