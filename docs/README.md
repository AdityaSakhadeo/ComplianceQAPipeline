# GitHub Pages site

Static demo UI for **Compliance QA Pipeline**.

## Enable Pages

1. Repository **Settings → Pages**.
2. **Build and deployment**: Source **Deploy from a branch**.
3. Branch **master** (or **main**), folder **`/docs`**, Save.
4. After build, open **https://adityasakhadeo.github.io/ComplianceQAPipeline/** (case-insensitive username).

## Pipeline image

`assets/pipeline-architecture.png` — architecture diagram (input → processing → demo output).

## Backend connection

GitHub Pages only hosts static files. To call your Python pipeline:

1. Deploy an HTTP API (e.g. Azure App Service, Container Apps, or FastAPI behind a URL).
2. Enable **CORS** for your Pages origin (`https://<user>.github.io`).
3. Edit **`js/config.js`**:

```js
window.COMPLIANCE_QA_CONFIG = {
  apiBaseUrl: "https://your-api.example.com",
  useMockQuotaMessage: false,
  auditPath: "/api/audit",
};
```

4. Implement `POST /api/audit` with JSON body `{ "video_url": "..." }` returning your audit JSON.

While `useMockQuotaMessage` is `true` or `apiBaseUrl` is empty, **Analyze** shows the static quota message (safe public demo).
