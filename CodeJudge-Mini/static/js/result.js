document.addEventListener("DOMContentLoaded", function () {
  const root = document.getElementById("result-app");
  if (!root) return;
  const id = root.dataset.submissionId;
  const label = (value) => String(value || "UNKNOWN").replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
  const badge = (status) => `<span class="badge badge-${String(status).toLowerCase().replaceAll("_", "-")}"><span class="badge-dot"></span>${label(status)}</span>`;
  const escapeHtml = (text) => String(text).replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;", "'":"&#39;"}[c]));

  function render(data) {
    const active = data.status === "PENDING" || data.status === "RUNNING";
    const cases = data.results || [];
    const timeline = `<div class="timeline"><span class="timeline-step done">PENDING</span><span>→</span><span class="timeline-step ${data.scheduler_state === "RUNNING" ? "current" : "done"}">RUNNING</span><span>→</span><span class="timeline-step ${active ? "" : "current"}">${active ? "VERDICT" : label(data.status)}</span></div>`;
    const caseHtml = cases.length ? cases.map((item, index) => `<div class="testcase-row"><div><strong>Test case ${index + 1}</strong><div class="cell-muted">${item.test_id}</div></div>${badge(item.status)}</div>${item.status !== "ACCEPTED" ? `<div class="io-compare"><div><div class="section-label">Expected</div><pre class="sample-box">${escapeHtml(item.expected_output || "")}</pre></div><div><div class="section-label">Actual</div><pre class="sample-box">${escapeHtml(item.actual_output || "")}</pre></div></div>` : ""}`).join("") : `<p class="cell-muted">Test-case rows appear after the worker commits the verdict.</p>`;
    root.innerHTML = `<div class="card card-padded"><div class="result-top">${badge(data.status)}<span class="cell-muted">${data.title || ""}</span></div>${timeline}<div class="result-summary"><div class="stat-box"><div class="stat-label">Scheduler state</div><div class="stat-value small">${label(data.scheduler_state)}</div></div><div class="stat-box"><div class="stat-label">Execution time</div><div class="stat-value small">${Number(data.execution_time || 0).toFixed(3)}s</div></div><div class="stat-box"><div class="stat-label">Waiting time</div><div class="stat-value small">${data.waiting_time == null ? "—" : Number(data.waiting_time).toFixed(3) + "s"}</div></div><div class="stat-box"><div class="stat-label">Turnaround</div><div class="stat-value small">${data.turnaround_time == null ? "—" : Number(data.turnaround_time).toFixed(3) + "s"}</div></div></div>${active ? `<div class="notice">The single background worker is processing this submission. This page checks again in one second.</div>` : ""}</div><div class="card card-padded"><h2>Per-test-case results</h2>${caseHtml}</div>`;
    document.getElementById("result-subtitle").textContent = active ? "Queued or running" : `${label(data.status)} · persisted result`;
    if (active) setTimeout(load, 1000);
  }
  function load() { fetch(`/api/submissions/${id}`).then(r => r.json()).then(render).catch(() => setTimeout(load, 1500)); }
  load();
});
