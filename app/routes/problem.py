from flask import Blueprint, abort, render_template, request, session
from app.database.queries import get_problem_attempts, get_problem_detail
from app.routes.common import login_required

problem_bp = Blueprint("problem", __name__)


@problem_bp.route("/problem")
@login_required
def problem():
    try:
        problem_id = int(request.args.get("id", "0"))
    except ValueError:
        abort(404)
    problem = get_problem_detail(problem_id)
    if problem is None:
        abort(404)
    attempts = get_problem_attempts(session["user_id"], problem_id)
    return render_template("problem.html", problem=problem, attempts=attempts)
