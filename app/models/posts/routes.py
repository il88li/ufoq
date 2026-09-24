from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.post_service import PostService

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    error = None
    if request.method == "POST":
        try:
            post = PostService.create(
                author=current_user,
                body=request.form.get("body", ""),
                image_url=request.form.get("image_url", ""),
                category=request.form.get("category", "general"),
                is_public=request.form.get("is_public", "1") == "1",
            )
            flash("تم نشر البرومبت", "success")
            return redirect(url_for("posts.detail", post_id=post.id))
        except ValueError as e:
            error = str(e)
    return render_template("posts/create.html", error=error)


@posts_bp.route("/<int:post_id>")
def detail(post_id):
    post = PostService.get(post_id)
    if not post or (not post.is_public and (not current_user.is_authenticated or current_user.id != post.author_id)):
        flash("المنشور غير موجود", "error")
        return redirect(url_for("feed.home"))
    return render_template("posts/detail.html", post=post)


@posts_bp.route("/<int:post_id>/copy", methods=["POST"])
def copy(post_id):
    post = PostService.get(post_id)
    if not post:
        return jsonify({"ok": False}), 404
    count = PostService.copy(post)
    return jsonify({"ok": True, "copy_count": count, "body": post.body})


@posts_bp.route("/<int:post_id>/like", methods=["POST"])
@login_required
def like(post_id):
    post = PostService.get(post_id)
    if not post:
        return jsonify({"ok": False}), 404
    liked = PostService.toggle_like(current_user, post)
    return jsonify({"ok": True, "liked": liked, "like_count": post.like_count})


@posts_bp.route("/<int:post_id>/save", methods=["POST"])
@login_required
def save(post_id):
    post = PostService.get(post_id)
    if not post:
        return jsonify({"ok": False}), 404
    saved = PostService.toggle_save(current_user, post)
    return jsonify({"ok": True, "saved": saved, "save_count": post.save_count})


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = PostService.get(post_id)
    if not post:
        flash("غير موجود", "error")
        return redirect(url_for("feed.home"))
    try:
        PostService.delete(post, current_user)
        flash("تم الحذف", "success")
    except PermissionError:
        flash("غير مسموح", "error")
    return redirect(url_for("feed.home"))