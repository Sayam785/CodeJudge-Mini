"""Flask application factory."""

from flask import Flask, render_template


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    from config import SECRET_KEY

    app.secret_key = SECRET_KEY

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.problems import problems_bp
    from app.routes.problem import problem_bp
    from app.routes.submit import submit_bp
    from app.routes.result import result_bp
    from app.routes.history import history_bp
    from app.routes.os_monitor import os_monitor_bp
    from app.routes.analytics import analytics_bp

    for blueprint in (
        auth_bp, dashboard_bp, problems_bp, problem_bp, submit_bp,
        result_bp, history_bp, os_monitor_bp, analytics_bp,
    ):
        app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app
