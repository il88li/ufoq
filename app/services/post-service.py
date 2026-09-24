from app.extensions import db
from app.models import Post, Like, Save


class PostService:
    @staticmethod
    def create(author, body: str, image_url: str = "", category: str = "general", is_public: bool = True):
        body = (body or "").strip()
        if not body:
            raise ValueError("نص المنشور مطلوب")
        post = Post(
            author_id=author.id,
            body=body,
            image_url=(image_url or "").strip(),
            category=(category or "general").strip(),
            is_public=is_public,
        )
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def get(post_id: int):
        return Post.query.get(post_id)

    @staticmethod
    def copy(post: Post):
        post.copy_count = (post.copy_count or 0) + 1
        db.session.commit()
        return post.copy_count

    @staticmethod
    def toggle_like(user, post: Post) -> bool:
        existing = Like.query.filter_by(user_id=user.id, post_id=post.id).first()
        if existing:
            db.session.delete(existing)
            post.like_count = max(0, (post.like_count or 0) - 1)
            db.session.commit()
            return False
        db.session.add(Like(user_id=user.id, post_id=post.id))
        post.like_count = (post.like_count or 0) + 1
        db.session.commit()
        return True

    @staticmethod
    def toggle_save(user, post: Post) -> bool:
        existing = Save.query.filter_by(user_id=user.id, post_id=post.id).first()
        if existing:
            db.session.delete(existing)
            post.save_count = max(0, (post.save_count or 0) - 1)
            db.session.commit()
            return False
        db.session.add(Save(user_id=user.id, post_id=post.id))
        post.save_count = (post.save_count or 0) + 1
        db.session.commit()
        return True

    @staticmethod
    def delete(post: Post, user) -> None:
        if post.author_id != user.id:
            raise PermissionError("غير مسموح")
        Like.query.filter_by(post_id=post.id).delete()
        Save.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()