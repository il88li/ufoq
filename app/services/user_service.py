from app.extensions import db
from app.models import User, Follow


class UserService:
    @staticmethod
    def register(username: str, email: str, password: str, display_name: str = ""):
        username = (username or "").strip().lower()
        email = (email or "").strip().lower()
        display_name = (display_name or username).strip()
        if not username or not email or not password:
            raise ValueError("جميع الحقول مطلوبة")
        if User.query.filter_by(username=username).first():
            raise ValueError("اسم المستخدم مستخدم مسبقاً")
        if User.query.filter_by(email=email).first():
            raise ValueError("البريد مستخدم مسبقاً")
        user = User(username=username, email=email, display_name=display_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(login: str, password: str):
        login = (login or "").strip().lower()
        user = User.query.filter(
            (User.username == login) | (User.email == login)
        ).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter_by(username=(username or "").strip().lower()).first()

    @staticmethod
    def update_profile(user, display_name=None, bio=None, avatar_url=None, is_private=None):
        if display_name is not None:
            user.display_name = display_name.strip() or user.username
        if bio is not None:
            user.bio = (bio or "")[:300]
        if avatar_url is not None:
            user.avatar_url = (avatar_url or "").strip()
        if is_private is not None:
            user.is_private = bool(is_private)
        db.session.commit()
        return user

    @staticmethod
    def toggle_follow(follower, target) -> bool:
        if follower.id == target.id:
            raise ValueError("لا يمكن متابعة نفسك")
        existing = Follow.query.filter_by(
            follower_id=follower.id, following_id=target.id
        ).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return False
        db.session.add(Follow(follower_id=follower.id, following_id=target.id))
        db.session.commit()
        return True

    @staticmethod
    def is_following(follower, target) -> bool:
        if not follower or not target:
            return False
        return (
            Follow.query.filter_by(
                follower_id=follower.id, following_id=target.id
            ).first()
            is not None
        )
