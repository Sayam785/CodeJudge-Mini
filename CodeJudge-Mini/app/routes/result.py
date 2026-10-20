from flask import Blueprint, abort, jsonify, render_template, request, session

from app.database.queries import get_submission_detail
from app.os_engine.scheduler import queue_position, scheduler
from app.routes.common import login_required

result_bp = Blueprint("result", __name__)


def _payload(submission_id):
    detail = get_submission_detail(session["user_id"], submission_id)
    if detail is None:
        return None
    row = detail["submission"]
    job_entry = scheduler.jobs().get(row[0], {})
    return {
        "submission_id": row[0], "problem_id": row[1], "title": row[2],
        "status": row[3], "execution_time": row[4],
        "submitted_at": row[5].isoformat() if row[5] else None,
        "queue_position": queue_position(row[0]),
        "scheduler_state": scheduler.state(row[0]) or row[3],
        "waiting_time": job_entry.get("waiting_time"),
        "run_time": job_entry.get("run_time"),
        "turnaround_time": job_entry.get("turnaround_time"),
        "results": detail["results"],
    }


@result_bp.route("/result")
@login_required
def result():
    try:
        submission_id = int(request.args.get("id", "0"))
    except ValueError:
        abort(404)
    if _payload(submission_id) is None:
        abort(404)
    return render_template("result.html", submission_id=submission_id)


@result_bp.route("/api/submissions/<int:submission_id>")
@login_required
def result_api(submission_id):
    payload = _payload(submission_id)
    if payload is None:
        return jsonify({"error": "Submission not found"}), 404
    return jsonify(payload)
