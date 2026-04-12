# Site (`docs/`)

Portfolio UI for **EKIP RAG** and **Compliance QA**. Both features call **your deployed APIs**; set base URLs in **`js/config.js`**.

## Host this folder

In the repository **Settings → Pages**, deploy from branch **`main`** or **`master`**, folder **`/docs`**.

## Assets

- `assets/ekip-architecture.png` — RAG pipeline diagram.
- `assets/pipeline-architecture.png` — compliance pipeline diagram.

## Backends

- **RAG:** `POST /api/rag/query` with JSON `{ "question": "..." }`. Deploy with Docker or `uvicorn` — see **`../enterprise-rag-platform/DEPLOY-FREE.md`**.
- **Compliance:** `POST /api/audit` with `{ "video_url": "..." }`.

Enable **CORS** on each API for your site origin (e.g. `https://<user>.github.io`).
