
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.database.queries import create_user, get_user_by_username

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)

        if user and check_password_hash(user[3], password):
            session.clear()
            session["user_id"] = int(user[0])
            session["username"] = user[1]
            return redirect(url_for("dashboard.dashboard"))

        return render_template("login.html", error="Invalid username or password.", username=username)

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(username) < 3 or len(username) > 50:
            return render_template("register.html", error="Username must be 3-50 characters.")
        if "@" not in email or len(email) > 100:
            return render_template("register.html", error="Enter a valid email address.")
        if len(password) < 6:
            return render_template("register.html", error="Password must contain at least 6 characters.")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        try:
            create_user(username, email, generate_password_hash(password))
        except Exception:
            return render_template("register.html", error="Username or email is already registered.")
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
