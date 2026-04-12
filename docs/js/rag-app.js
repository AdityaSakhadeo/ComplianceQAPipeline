(function () {
  const ragCfg = window.EKIP_RAG_CONFIG || {};

  const form = document.getElementById("rag-form");
  const textarea = document.getElementById("rag-question");
  const submitBtn = document.getElementById("rag-submit-btn");
  if (!form || !textarea || !submitBtn) return;

  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");
  const alertEl = document.getElementById("rag-alert-error");
  const errMsg = document.getElementById("rag-error-msg");
  const resultEl = document.getElementById("rag-result");
  const answerEl = document.getElementById("rag-answer-text");
  const citationsEl = document.getElementById("rag-citations-pre");

  function setRagLoading(loading) {
    submitBtn.disabled = loading;
    if (btnText) btnText.hidden = loading;
    if (btnSpinner) btnSpinner.hidden = !loading;
  }

  function hideRagAlerts() {
    if (alertEl) alertEl.hidden = true;
    if (resultEl) resultEl.hidden = true;
  }

  function showResult(payload) {
    if (!resultEl || !answerEl || !citationsEl) return;
    answerEl.textContent = payload.answer || "";
    citationsEl.textContent = payload.citations || "(no citation block)";
    resultEl.hidden = false;
  }

  document.querySelectorAll("[data-rag-suggest]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = btn.getAttribute("data-rag-suggest");
      if (t) {
        textarea.value = t;
        textarea.focus();
      }
    });
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideRagAlerts();

    const question = textarea.value.trim();
    if (!question) {
      textarea.focus();
      return;
    }

    const base = String(ragCfg.ragApiBaseUrl || "").replace(/\/$/, "");
    if (!base) {
      if (errMsg && alertEl) {
        errMsg.textContent =
          "Set ragApiBaseUrl in js/config.js to your deployed RAG API URL (see enterprise-rag-platform/DEPLOY-FREE.md).";
        alertEl.hidden = false;
      }
      return;
    }

    const path = ragCfg.ragQueryPath || "/api/rag/query";
    const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

    setRagLoading(true);

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          top_k: ragCfg.ragTopK || 5,
          use_llm: ragCfg.ragUseLlm !== false,
        }),
      });
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }
      if (!res.ok) {
        const d = data && data.detail;
        let msg;
        if (typeof d === "string") msg = d;
        else if (Array.isArray(d))
          msg = d.map((x) => (x && x.msg) || JSON.stringify(x)).join("; ");
        else msg = (data && data.message) || text || res.statusText;
        throw new Error(msg);
      }
      showResult({
        answer: data.answer || "",
        citations: data.citations || "",
      });
    } catch (err) {
      if (errMsg && alertEl) {
        errMsg.textContent =
          err.message ||
          "Network error — check CORS and that the RAG API is reachable.";
        alertEl.hidden = false;
      }
    } finally {
      setRagLoading(false);
    }
  });
})();
