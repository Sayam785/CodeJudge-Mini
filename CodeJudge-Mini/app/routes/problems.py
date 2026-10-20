from flask import Blueprint, render_template, request
from app.database.queries import get_problems
from app.routes.common import login_required

problems_bp = Blueprint("problems", __name__)


@problems_bp.route("/problems")
@login_required
def problems():
    problems = get_problems()
    search = request.args.get("q", "").strip().lower()
    if search:
        problems = [p for p in problems if search in str(p[1]).lower()]
    return render_template("problems.html", problems=problems, search=search)
