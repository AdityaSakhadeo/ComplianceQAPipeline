/**
 * Production API endpoints for this site. Set base URLs after you deploy.
 * RAG: see enterprise-rag-platform/DEPLOY-FREE.md and Dockerfile.
 */
window.COMPLIANCE_QA_CONFIG = {
  apiBaseUrl: "",
  auditPath: "/api/audit",
};

window.EKIP_RAG_CONFIG = {
  ragApiBaseUrl: "",
  ragQueryPath: "/api/rag/query",
  ragTopK: 5,
  ragUseLlm: true,
};
