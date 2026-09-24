from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.services.feed_service import FeedService

profiles_bp = Blueprint("profiles", __name__, url_prefix="/u")


@profiles_bp.route("/<username>")
def view(username):
    user = UserService.get_by_username(username)
    if not user:
        flash("المستخدم غير موجود", "error")
        return redirect(url_for("feed.home"))
    page = request.args.get("page", 1, type=int)
    pagination = FeedService.by_user(user.id, page=page, viewer=current_user)
    following = (
        UserService.is_following(current_user, user)
        if current_user.is_authenticated
        else False
    )
    return render_template(
        "profiles/view.html",
        profile=user,
        posts=pagination.items,
        pagination=pagination,
        following=following,
    )


@profiles_bp.route("/<username>/follow", methods=["POST"])
@login_required
def follow(username):
    target = UserService.get_by_username(username)
    if not target:
        flash("غير موجود", "error")
        return redirect(url_for("feed.home"))
    try:
        now = UserService.toggle_follow(current_user, target)
        flash("تمت المتابعة" if now else "أُلغيت المتابعة", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("profiles.view", username=username))
