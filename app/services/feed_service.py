from app.models import Post, Follow


class FeedService:
    @staticmethod
    def public(page: int = 1, per_page: int = 20):
        return (
            Post.query.filter_by(is_public=True)
            .order_by(Post.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def following(user, page: int = 1, per_page: int = 20):
        ids = Follow.following_ids(user.id)
        if not ids:
            return (
                Post.query.filter_by(id=-1)
                .paginate(page=page, per_page=per_page, error_out=False)
            )
        return (
            Post.query.filter(Post.author_id.in_(ids), Post.is_public.is_(True))
            .order_by(Post.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    @staticmethod
    def by_user(user_id: int, page: int = 1, per_page: int = 20, viewer=None):
        q = Post.query.filter_by(author_id=user_id)
        if not viewer or viewer.id != user_id:
            q = q.filter_by(is_public=True)
        return q.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
