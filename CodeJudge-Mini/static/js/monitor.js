document.addEventListener("DOMContentLoaded", function () {
  const rows = document.getElementById("monitor-rows");
  if (!rows) return;
  function refresh() {
    fetch("/api/os-monitor").then(r => r.json()).then(data => {
      document.querySelector('[data-field="queue_length"]').textContent = data.queue_length;
      document.querySelector('[data-field="worker"]').textContent = data.worker_alive ? "Alive" : "Stopped";
      document.querySelector('[data-field="completed"]').textContent = data.metrics.completed;
      document.querySelector('[data-field="average_waiting"]').textContent = Number(data.average_waiting_time || 0).toFixed(3) + "s";
      rows.innerHTML = data.jobs.length ? data.jobs.map(job => `<tr><td>#${job.submission_id}</td><td>${job.problem_id}</td><td>${String(job.state).replaceAll("_", " ")}</td><td>${job.waiting_time == null ? "—" : Number(job.waiting_time).toFixed(3) + "s"}</td><td>${job.turnaround_time == null ? "—" : Number(job.turnaround_time).toFixed(3) + "s"}</td></tr>`).join("") : '<tr><td colspan="5" class="empty-state">No jobs have been scheduled in this process.</td></tr>';
      setTimeout(refresh, 1000);
    }).catch(() => setTimeout(refresh, 2000));
  }
  setTimeout(refresh, 1000);
});
