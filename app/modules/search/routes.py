from flask import Blueprint, render_template, request
from app.services.search_service import SearchService

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    kind = request.args.get("kind", "posts")
    page = request.args.get("page", 1, type=int)
    posts_page = users_page = None
    if q:
        if kind == "users":
            users_page = SearchService.users(q, page=page)
        else:
            kind = "posts"
            posts_page = SearchService.posts(q, page=page)
    return render_template(
        "search/index.html",
        q=q,
        kind=kind,
        posts_page=posts_page,
        users_page=users_page,
    )
