(function () {
  const ragCfg = window.EKIP_RAG_CONFIG || {};

  const DEMO_SCENARIOS = [
    {
      suggest:
        "What was the company's operating result in its first reporting period?",
      match: (q) =>
        /operating|loss|profit|financial|revenue|march\s*31.*2003|first.*report|crore/i.test(
          q,
        ),
      answer: `For the period ended March 31, 2003, the annual report shows revenue from business process management services of Rs. 20.85 crore, cost of revenues Rs. 14.49 crore, gross profit Rs. 6.36 crore, and an operating loss of Rs. 4.32 crore (depreciation Rs. 1.39 crore). After other items, loss after tax was Rs. 3.15 crore. [1]`,
      citations: `[1] annual-report-2002-2003.pdf (pages 3-3) — type=annual-report, year=2003`,
    },
    {
      suggest: "Who chaired the board in the early annual report?",
      match: (q) =>
        /board|chairman|director|mohandas|pai|akshaya|bhargava|auditors/i.test(q),
      answer: `The report lists Mr. T. V. Mohandas Pai as Chairman, Mr. Akshaya Bhargava as Managing Director and CEO, additional directors, and M/s Bharat S. Raut & Co. as auditors (Bangalore). [1][2]`,
      citations: `[1] annual-report-2002-2003.pdf (pages 2-2) — type=annual-report, year=2003\n[2] annual-report-2002-2003.pdf (pages 2-2) — type=annual-report, year=2003`,
    },
    {
      suggest: "Which industry verticals were mentioned for new customers?",
      match: (q) =>
        /customer|vertical|banking|telecom|financial\s*service|added/i.test(q),
      answer: `The company added three customers in banking and financial services and two in telecommunications during its first period of operations. [1]`,
      citations: `[1] annual-report-2002-2003.pdf (pages 3-3) — type=annual-report, year=2003`,
    },
  ];

  function pickDemo(question) {
    const q = question.trim();
    for (let i = 0; i < DEMO_SCENARIOS.length; i++) {
      const d = DEMO_SCENARIOS[i];
      if (d.match(q)) {
        return {
          mode: "demo",
          question: q,
          answer: d.answer,
          citations: d.citations,
        };
      }
    }
    return {
      mode: "demo_fallback",
      question: q,
      answer: `No scripted match for that exact wording. This browser demo uses fixed sample answers tied to the indexed annual-report corpus. For real vector retrieval and LLM synthesis, deploy the FastAPI service under enterprise-rag-platform and set ragApiBaseUrl in config.js.

Try one of these:
${DEMO_SCENARIOS.map((d) => "• " + d.suggest).join("\n")}`,
      citations: "",
    };
  }

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
  const modeNote = document.getElementById("rag-mode-note");

  function setRagLoading(loading) {
    submitBtn.disabled = loading;
    if (btnText) btnText.hidden = loading;
    if (btnSpinner) btnSpinner.hidden = !loading;
  }

  function hideRagAlerts() {
    if (alertEl) alertEl.hidden = true;
    if (resultEl) resultEl.hidden = true;
  }

  function showResult(payload, sourceLabel) {
    if (!resultEl || !answerEl || !citationsEl) return;
    answerEl.textContent = payload.answer || "";
    citationsEl.textContent = payload.citations || "(no citation block)";
    resultEl.hidden = false;
    if (modeNote) {
      modeNote.textContent = sourceLabel;
      modeNote.hidden = false;
    }
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
    const useLive =
      base.length > 0 && ragCfg.useRagMockOnly !== true;

    setRagLoading(true);

    if (!useLive) {
      await new Promise((r) => setTimeout(r, 400));
      const demo = pickDemo(question);
      showResult(
        demo,
        demo.mode === "demo"
          ? "Demo mode — sample answer (connect API for live RAG)"
          : "Demo mode — try a suggested question or deploy the API",
      );
      setRagLoading(false);
      return;
    }

    const path = ragCfg.ragQueryPath || "/api/rag/query";
    const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

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
      showResult(
        {
          answer: data.answer || "",
          citations: data.citations || "",
        },
        "Live API — Chroma retrieval + optional LLM",
      );
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
