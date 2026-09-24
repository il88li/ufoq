from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("feed.home"))
    error = None
    if request.method == "POST":
        try:
            user = UserService.register(
                username=request.form.get("username", ""),
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
                display_name=request.form.get("display_name", ""),
            )
            login_user(user)
            flash("مرحباً بك في خيال ✨", "success")
            return redirect(url_for("feed.home"))
        except ValueError as e:
            error = str(e)
    return render_template("auth/register.html", error=error)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("feed.home"))
    error = None
    if request.method == "POST":
        user = UserService.authenticate(
            request.form.get("login", ""),
            request.form.get("password", ""),
        )
        if user:
            login_user(user, remember=bool(request.form.get("remember")))
            next_url = request.args.get("next") or url_for("feed.home")
            return redirect(next_url)
        error = "بيانات الدخول غير صحيحة"
    return render_template("auth/login.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج", "info")
    return redirect(url_for("feed.home"))
