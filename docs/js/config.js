/**
 * GitHub Pages demo — wire your deployed backend here.
 * CORS must allow your GitHub Pages origin (or use an API gateway).
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
