from app.models import Post, User


class SearchService:
    @staticmethod
    def posts(q: str, page: int = 1, per_page: int = 20):
        q = (q or "").strip()
        if not q:
            return Post.query.filter_by(id=-1).paginate(
                page=page, per_page=per_page, error_out=False
            )
        pattern = f"%{q}%"
        return (
            Post.query.filter(
                Post.is_public.is_(True),
                (Post.body.ilike(pattern)) | (Post.category.ilike(pattern)),
            )
            .order_by(Post.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def users(q: str, page: int = 1, per_page: int = 20):
        q = (q or "").strip()
        if not q:
            return User.query.filter_by(id=-1).paginate(
                page=page, per_page=per_page, error_out=False
            )
        pattern = f"%{q}%"
        return (
            User.query.filter(
                (User.username.ilike(pattern))
                | (User.display_name.ilike(pattern))
                | (User.bio.ilike(pattern))
            )
            .order_by(User.username)
            .paginate(page=page, per_page=per_page, error_out=False)
        )
