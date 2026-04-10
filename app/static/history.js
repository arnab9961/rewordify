const historyPageList = document.getElementById("historyPageList");
const historyUserName = document.getElementById("historyUserName");
const historyUserEmail = document.getElementById("historyUserEmail");
const historyTotal = document.getElementById("historyTotal");
const historyLogoutBtn = document.getElementById("historyLogoutBtn");

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function truncateText(text, maxLength = 220) {
  if (!text) {
    return "";
  }
  return text.length > maxLength ? `${text.slice(0, maxLength).trim()}...` : text;
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

function renderGuest() {
  historyUserName.textContent = "Guest";
  historyUserEmail.textContent = "Sign in to view saved history.";
  historyTotal.textContent = "0";
  historyPageList.innerHTML = '<div class="history-empty">No history available yet.</div>';
}

function renderHistory(profile) {
  historyUserName.textContent = profile.user?.username || "Member";
  historyUserEmail.textContent = profile.user?.email || "";
  historyTotal.textContent = String(profile.total_history ?? 0);

  const history = profile.recent_history || [];
  if (!history.length) {
    historyPageList.innerHTML = '<div class="history-empty">No saved history yet.</div>';
    return;
  }

  historyPageList.innerHTML = history.map((item) => `
    <article class="history-card">
      <div class="history-card-head">
        <span class="history-tool">${escapeHtml(item.tool || "tool")}</span>
        <span>${escapeHtml(formatHistoryDate(item.created_at))}</span>
      </div>
      <div class="history-preview"><strong>Input:</strong> ${escapeHtml(truncateText(item.input_text || ""))}</div>
      <div class="history-preview"><strong>Result:</strong> ${escapeHtml(truncateText(item.output_text || ""))}</div>
    </article>
  `).join("");
}

async function loadHistory() {
  try {
    const response = await fetch("/auth/me");
    if (!response.ok) {
      renderGuest();
      return;
    }

    const data = await response.json();
    renderHistory(data);
  } catch {
    renderGuest();
  }
}

async function logout() {
  try {
    await fetch("/auth/logout", { method: "POST" });
  } finally {
    window.location.href = "/login";
  }
}

if (historyLogoutBtn) {
  historyLogoutBtn.addEventListener("click", logout);
}

loadHistory();