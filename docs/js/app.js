const cfg = window.COMPLIANCE_QA_CONFIG || {};

const form = document.getElementById("audit-form");
const input = document.getElementById("video-url");
const submitBtn = document.getElementById("submit-btn");
const btnText = submitBtn.querySelector(".btn-text");
const btnSpinner = submitBtn.querySelector(".btn-spinner");
const modalQuota = document.getElementById("modal-quota");
const alertApi = document.getElementById("alert-api-error");
const apiErrorMsg = document.getElementById("api-error-msg");
const resultSuccess = document.getElementById("result-success");
const resultJson = document.getElementById("result-json");

function setLoading(loading) {
  submitBtn.disabled = loading;
  btnText.hidden = loading;
  btnSpinner.hidden = !loading;
}

function openQuotaModal() {
  modalQuota.hidden = false;
  document.body.classList.add("modal-open");
  const closeBtn = modalQuota.querySelector(".modal-close");
  closeBtn.focus();
}

function closeQuotaModal() {
  modalQuota.hidden = true;
  document.body.classList.remove("modal-open");
}

modalQuota.querySelectorAll("[data-close-modal]").forEach((el) => {
  el.addEventListener("click", () => closeQuotaModal());
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modalQuota.hidden) {
    closeQuotaModal();
  }
});

function hideAlerts() {
  closeQuotaModal();
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

  const useMock =
    cfg.useMockQuotaMessage !== false ||
    !cfg.apiBaseUrl ||
    String(cfg.apiBaseUrl).trim() === "";

  setLoading(true);

  if (useMock) {
    await new Promise((r) => setTimeout(r, 650));
    setLoading(false);
    openQuotaModal();
    return;
  }

  const base = String(cfg.apiBaseUrl).replace(/\/$/, "");
  const path = cfg.auditPath || "/api/audit";
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

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
