from flask import Blueprint, render_template, request, session

from app.database.queries import get_history_page
from app.routes.common import login_required

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
@login_required
def history():
    status = request.args.get("status", "").strip().upper() or None
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    rows, total = get_history_page(session["user_id"], status, page)
    return render_template(
        "history.html", history=rows, status=status or "", page=page,
        total_pages=max(1, (total + 9) // 10),
    )
