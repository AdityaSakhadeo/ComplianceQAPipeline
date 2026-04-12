const cfg = window.COMPLIANCE_QA_CONFIG || {};

const form = document.getElementById("audit-form");
const input = document.getElementById("video-url");
const submitBtn = document.getElementById("submit-btn");
const btnText = submitBtn.querySelector(".btn-text");
const btnSpinner = submitBtn.querySelector(".btn-spinner");
const alertApi = document.getElementById("alert-api-error");
const apiErrorMsg = document.getElementById("api-error-msg");
const resultSuccess = document.getElementById("result-success");
const resultJson = document.getElementById("result-json");

function setLoading(loading) {
  submitBtn.disabled = loading;
  btnText.hidden = loading;
  btnSpinner.hidden = !loading;
}

function hideAlerts() {
  alertApi.hidden = true;
  resultSuccess.hidden = true;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlerts();

  const videoUrl = input.value.trim();
  if (!videoUrl) {
    input.focus();
    return;
  }

  const base = String(cfg.apiBaseUrl || "").replace(/\/$/, "");
  if (!base) {
    apiErrorMsg.textContent =
      "Set apiBaseUrl in js/config.js to your deployed compliance API.";
    alertApi.hidden = false;
    return;
  }

  const path = cfg.auditPath || "/api/audit";
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

  setLoading(true);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_url: videoUrl }),
    });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
    if (!res.ok) {
      throw new Error(data.detail || data.message || text || res.statusText);
    }
    resultJson.textContent = JSON.stringify(data, null, 2);
    resultSuccess.hidden = false;
  } catch (err) {
    apiErrorMsg.textContent =
      err.message ||
      "Network error — check CORS and that the API is reachable.";
    alertApi.hidden = false;
  } finally {
    setLoading(false);
  }
});
