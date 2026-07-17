from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token

from career_compass.models import User, db
from career_compass.utils import validate_login_data, validate_registration_data

main_bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to access the dashboard.", "warning")
            return redirect(url_for("main.login"))
        return view(**kwargs)
    return wrapped_view


@main_bp.app_context_processor
def inject_current_user():
    return {"current_user": session.get("user_name")}


@main_bp.route("/", endpoint="home")
def home():
    return render_template("intro.html")


@main_bp.route("/landing", endpoint="landing")
def landing():
    return render_template("index.html")


@main_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = validate_login_data(email, password)

        if not errors:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                token = create_access_token(identity=str(user.id))
                session.clear()
                session["user_id"] = user.id
                session["user_name"] = user.full_name.split()[0]
                session["role"] = user.role
                session["jwt_token"] = token
                flash("Welcome back! Your career dashboard is ready.", "success")
                return redirect(url_for("main.dashboard"))
            errors["authentication"] = "Incorrect email or password."

        for message in errors.values():
            flash(message, "danger")

    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_registration_data(full_name, email, password, confirm_password)
        if not errors:
            user = User(full_name=full_name, email=email, role="student")
            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
                token = create_access_token(identity=str(user.id))
                session.clear()
                session["user_id"] = user.id
                session["user_name"] = user.full_name.split()[0]
                session["role"] = user.role
                session["jwt_token"] = token
                flash("Account created successfully. Welcome aboard!", "success")
                return redirect(url_for("main.dashboard"))
            except IntegrityError:
                db.session.rollback()
                flash("An account with this email already exists.", "danger")
        else:
            for message in errors.values():
                flash(message, "danger")

    return render_template("register.html")


@main_bp.route("/dashboard", endpoint="dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/resume", endpoint="resume")
@login_required
def resume():
    return render_template("resume.html")


@main_bp.route("/career", endpoint="career")
@login_required
def career():
    return render_template("career.html")


@main_bp.route("/chatbot", endpoint="chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html")


@main_bp.route("/admin", endpoint="admin")
@login_required
def admin():
    if session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("main.dashboard"))
    return render_template("admin.html")


@main_bp.route("/logout", endpoint="logout")
def logout():
    session.clear()
    flash("You have been logged out safely.", "success")
    return redirect(url_for("home"))
