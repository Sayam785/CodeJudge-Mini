from flask import Blueprint, render_template

from app.database.queries import get_analytics
from app.routes.common import login_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def analytics():
    per_problem, top_users = get_analytics()
    return render_template("analytics.html", per_problem=per_problem, top_users=top_users)
