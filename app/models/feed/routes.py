from flask import Blueprint, render_template, request
from flask_login import current_user
from app.services.feed_service import FeedService
from app.models import Like, Save

feed_bp = Blueprint("feed", __name__)


def _enrich(posts, user):
    liked, saved = set(), set()
    if user and user.is_authenticated and posts:
        ids = [p.id for p in posts]
        liked = {
            r.post_id
            for r in Like.query.filter(Like.user_id == user.id, Like.post_id.in_(ids)).all()
        }
        saved = {
            r.post_id
            for r in Save.query.filter(Save.user_id == user.id, Save.post_id.in_(ids)).all()
        }
    return liked, saved


@feed_bp.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    tab = request.args.get("tab", "all")
    if tab == "following" and current_user.is_authenticated:
        pagination = FeedService.following(current_user, page=page)
    else:
        tab = "all"
        pagination = FeedService.public(page=page)
    liked, saved = _enrich(pagination.items, current_user)
    return render_template(
        "feed/home.html",
        posts=pagination.items,
        pagination=pagination,
        tab=tab,
        liked_ids=liked,
        saved_ids=saved,
    )