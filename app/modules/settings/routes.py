from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.user_service import UserService

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        UserService.update_profile(
            current_user,
            display_name=request.form.get("display_name"),
            bio=request.form.get("bio"),
            avatar_url=request.form.get("avatar_url"),
            is_private=request.form.get("is_private") == "1",
        )
        flash("تم حفظ الإعدادات", "success")
        return redirect(url_for("settings.index"))
    return render_template("settings/index.html")