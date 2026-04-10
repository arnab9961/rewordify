const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const tone = document.getElementById("tone");
const creativity = document.getElementById("creativity");
const format = document.getElementById("format");
const audience = document.getElementById("audience");
const purpose = document.getElementById("purpose");
const preserveMeaning = document.getElementById("preserveMeaning");
const preserveMeaningParaphrase = document.getElementById("preserveMeaningParaphrase");
const paraphraseMode = document.getElementById("paraphraseMode");
const rewriteBtn = document.getElementById("rewriteBtn");
const copyBtn = document.getElementById("copyBtn");
const statusEl = document.getElementById("status");
const resultHeading = document.getElementById("resultHeading");
const resultSubtext = document.getElementById("resultSubtext");
const heroActions = document.querySelector(".hero-actions");
const guestActions = document.getElementById("guestActions");
const profileMenu = document.getElementById("profileMenu");
const profileTrigger = document.getElementById("profileTrigger");
const profileTriggerName = document.getElementById("profileTriggerName");
const menuLogoutBtn = document.getElementById("menuLogoutBtn");
const toolTabs = document.querySelectorAll(".tool-tab");
const rewriterControls = document.querySelectorAll(".tool-rewriter");
const paraphraseControls = document.querySelectorAll(".tool-paraphrase");
const aiGraph = document.getElementById("aiGraph");
const aiPercent = document.getElementById("aiPercent");
const humanPercent = document.getElementById("humanPercent");
const aiMeterFill = document.getElementById("aiMeterFill");
const humanMeterFill = document.getElementById("humanMeterFill");
const aiVerdict = document.getElementById("aiVerdict");
const INPUT_CACHE_KEY = "rewordify_input_text";
let activeTool = "rewriter";

function setStatus(message, type = "") {
  statusEl.textContent = message;
  statusEl.classList.remove("error", "loading");
  if (type) {
    statusEl.classList.add(type);
  }
}

function setTool(tool) {
  activeTool = tool;
  toolTabs.forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.tool === tool);
  });

  const isRewriter = tool === "rewriter";
  const isParaphrase = tool === "paraphrase";
  const isAIDetector = tool === "ai-detector";

  rewriterControls.forEach((el) => el.classList.toggle("is-hidden", !isRewriter));
  paraphraseControls.forEach((el) => el.classList.toggle("is-hidden", !isParaphrase));
  aiGraph.classList.toggle("is-hidden", !isAIDetector);

  if (isRewriter) {
    rewriteBtn.textContent = "Rewrite Now";
    resultHeading.textContent = "Rewritten Result";
    resultSubtext.textContent = "Smartly refined output from your model.";
  } else if (isParaphrase) {
    rewriteBtn.textContent = "Paraphrase Now";
    resultHeading.textContent = "Paraphrased Result";
    resultSubtext.textContent = "Alternative wording with preserved intent.";
  } else {
    rewriteBtn.textContent = "Detect AI";
    resultHeading.textContent = "AI Detection Result";
    resultSubtext.textContent = "Estimated AI-likelihood from writing signals.";
  }
}

function renderAIGraph(aiScore, humanScore, verdict, summary) {
  aiPercent.textContent = `${aiScore}%`;
  humanPercent.textContent = `${humanScore}%`;
  aiMeterFill.style.width = `${aiScore}%`;
  humanMeterFill.style.width = `${humanScore}%`;
  aiVerdict.textContent = `${verdict}. ${summary}`;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatHistoryDate(value) {
  if (!value) {
    return "Recent";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Recent"
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function renderGuestProfile() {
  guestActions.classList.remove("is-hidden");
  profileMenu.classList.add("is-hidden");
  profileTriggerName.textContent = "Guest";
}

function renderProfile(profile) {
  guestActions.classList.add("is-hidden");
  profileMenu.classList.remove("is-hidden");
  const username = profile.user?.username || "Member";
  profileTriggerName.textContent = username;
}

async function loadProfile() {
  try {
    const response = await fetch("/auth/me");
    if (!response.ok) {
      renderGuestProfile();
      return false;
    }

    const data = await response.json();
    renderProfile(data);
    return true;
  } catch {
    renderGuestProfile();
    return false;
  }
}

async function logout() {
  try {
    await fetch("/auth/logout", { method: "POST" });
  } finally {
    window.location.href = "/login";
  }
}

async function runTool() {
  const text = inputText.value.trim();
  if (!text) {
    setStatus("Please add text first.", "error");
    return;
  }

  rewriteBtn.disabled = true;
  rewriteBtn.textContent = "Processing...";
  setStatus("Contacting model...", "loading");

  try {
    let url = "/rewriter/rewrite";
    let payload = { text };

    if (activeTool === "rewriter") {
      payload = {
        text,
        tone: tone.value,
        creativity: creativity.value,
        output_format: format.value,
        audience: audience.value.trim() || null,
        purpose: purpose.value.trim() || null,
        preserve_meaning: preserveMeaning.checked,
      };
    } else if (activeTool === "paraphrase") {
      url = "/paraphrase";
      payload = {
        text,
        mode: paraphraseMode.value,
        preserve_meaning: preserveMeaningParaphrase.checked,
      };
    } else {
      url = "/ai-detector";
    }

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Rewrite failed.");
    }

    if (activeTool === "rewriter") {
      outputText.value = data.rewritten_text || "";
      setStatus("Rewrite complete.");
    } else if (activeTool === "paraphrase") {
      outputText.value = data.paraphrased_text || "";
      setStatus("Paraphrase complete.");
    } else {
      const aiScore = data.ai_score ?? 0;
      const humanScore = data.human_score ?? 100;
      renderAIGraph(aiScore, humanScore, data.verdict || "Mixed signals", data.summary || "");
      outputText.value = `${data.verdict || "Mixed signals"}\n\nAI Score: ${aiScore}%\nHuman Score: ${humanScore}%\n\n${data.summary || ""}`;
      setStatus("AI detection complete.");
    }

    await loadProfile();
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  } finally {
    rewriteBtn.disabled = false;
    setTool(activeTool);
  }
}

function copyOutput() {
  const text = outputText.value;
  if (!text) {
    setStatus("Nothing to copy yet.", "error");
    return;
  }

  navigator.clipboard.writeText(text)
    .then(() => setStatus("Copied to clipboard."))
    .catch(() => setStatus("Unable to copy automatically.", "error"));
}

rewriteBtn.addEventListener("click", runTool);
copyBtn.addEventListener("click", copyOutput);
if (menuLogoutBtn) {
  menuLogoutBtn.addEventListener("click", logout);
}
toolTabs.forEach((tab) => {
  tab.addEventListener("click", () => setTool(tab.dataset.tool));
});

const cachedInput = localStorage.getItem(INPUT_CACHE_KEY);
if (cachedInput) {
  inputText.value = cachedInput;
}

inputText.addEventListener("input", () => {
  localStorage.setItem(INPUT_CACHE_KEY, inputText.value);
});

setTool("rewriter");
loadProfile();
