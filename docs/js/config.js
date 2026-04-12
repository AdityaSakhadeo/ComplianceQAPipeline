/**
 * Portfolio wiring. See enterprise-rag-platform/DEPLOY-FREE.md and STREAMLIT.md.
 */
window.COMPLIANCE_QA_CONFIG = {
  apiBaseUrl: "",
  auditPath: "/api/audit",
};

window.EKIP_RAG_CONFIG = {
  /** Public Streamlit app URL (e.g. https://xxx.streamlit.app) — no trailing slash */
  streamlitRagUrl: "",
  /** Optional: FastAPI base URL for in-page REST demo */
  ragApiBaseUrl: "",
  ragQueryPath: "/api/rag/query",
  ragTopK: 5,
  ragUseLlm: true,
};
