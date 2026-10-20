from flask import Blueprint, render_template, session

from app.database.queries import get_dashboard_stats, get_recent_submissions
from app.routes.common import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    return render_template(
        "dashboard.html",
        stats=get_dashboard_stats(user_id),
        recent=get_recent_submissions(user_id),
    )
