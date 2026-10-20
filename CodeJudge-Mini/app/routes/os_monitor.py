from flask import Blueprint, jsonify, render_template

from app.os_engine.scheduler import average_waiting_time, metrics, pending_jobs, queue_position, scheduler
from app.os_engine.worker import worker
from app.routes.common import login_required

os_monitor_bp = Blueprint("os_monitor", __name__)


def monitor_payload():
    entries = []
    for submission_id, entry in scheduler.jobs().items():
        job = entry["job"]
        entries.append({
            "submission_id": submission_id,
            "problem_id": job.problem_id,
            "state": entry.get("state", "PENDING"),
            "queue_position": queue_position(submission_id),
            "waiting_time": entry.get("waiting_time"),
            "run_time": entry.get("run_time"),
            "turnaround_time": entry.get("turnaround_time"),
        })
    entries.sort(key=lambda row: row["submission_id"], reverse=True)
    return {
        "queue_length": pending_jobs(),
        "worker_alive": bool(worker() and worker().is_alive()),
        "jobs": entries[:20],
        "metrics": metrics(),
        "average_waiting_time": average_waiting_time(),
    }


@os_monitor_bp.route("/os-monitor")
@login_required
def monitor():
    return render_template("os_monitor.html", data=monitor_payload())


@os_monitor_bp.route("/api/os-monitor")
@login_required
def monitor_api():
    return jsonify(monitor_payload())
