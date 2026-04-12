/**
 * GitHub Pages demo — wire your deployed backends here.
 * CORS must allow your GitHub Pages origin on each API.
 */
window.COMPLIANCE_QA_CONFIG = {
  /** e.g. "https://your-app.azurewebsites.net" — no trailing slash */
  apiBaseUrl: "",
  /**
   * true: show static "out of quota" message (default for public demo).
   * false: POST to apiBaseUrl + auditPath with { video_url }.
   */
  useMockQuotaMessage: true,
  auditPath: "/api/audit",
};

/** Enterprise Knowledge Intelligence Platform (RAG) */
window.EKIP_RAG_CONFIG = {
  /**
   * e.g. "https://your-rag-api.azurewebsites.net" — no trailing slash.
   * Empty: browser uses scripted demo answers (see rag-app.js).
   */
  ragApiBaseUrl: "",
  ragQueryPath: "/api/rag/query",
  ragTopK: 5,
  ragUseLlm: true,
  /** Force demo even when ragApiBaseUrl is set (for testing). */
  useRagMockOnly: false,
};
