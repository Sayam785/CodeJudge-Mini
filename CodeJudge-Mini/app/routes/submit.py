from flask import Blueprint, flash, redirect, request, session, url_for

from config import MAX_SOURCE_BYTES
from app.database.queries import create_submission, get_problem_time_limit
from app.os_engine.queue import JobValidationError
from app.os_engine.scheduler import schedule_submission
from app.os_engine.worker import AdministratorExecutionError, start_worker
from app.routes.common import login_required

submit_bp = Blueprint("submit", __name__)


@submit_bp.route("/submit", methods=["POST"])
@login_required
def submit():
    source_code = request.form.get("source_code", "")
    try:
        problem_id = int(request.form.get("problem_id", "0"))
    except (TypeError, ValueError):
        flash("Choose a valid problem.", "error")
        return redirect(url_for("problems.problems"))

    if not source_code.strip():
        flash("Source code cannot be empty.", "error")
        return redirect(url_for("problem.problem", id=problem_id))
    if len(source_code.encode("utf-8")) > MAX_SOURCE_BYTES:
        flash("Source code must be 64 KB or smaller.", "error")
        return redirect(url_for("problem.problem", id=problem_id))

    time_limit = get_problem_time_limit(problem_id)
    if time_limit is None:
        flash("Problem not found.", "error")
        return redirect(url_for("problems.problems"))

    try:
        submission_id = create_submission(session["user_id"], problem_id, source_code)
        job = {
            "submission_id": submission_id,
            "problem_id": problem_id,
            "source_code": source_code,
            "time_limit": time_limit,
        }
        schedule_submission(job)
        start_worker()
    except Exception as exc:
        flash(f"Submission could not be queued: {exc}", "error")
        return redirect(url_for("problem.problem", id=problem_id))
    return redirect(url_for("result.result", id=submission_id))
