import os
from flask import Flask
from app.extensions import db, login_manager


def create_app():
    base = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base, "templates"),
        static_folder=os.path.join(base, "static"),
    )

    secret = os.getenv("SECRET_KEY") or "dev-secret-change-me"
    app.config["SECRET_KEY"] = secret

    db_url = (os.getenv("DATABASE_URL") or "").strip()
    if not db_url:
        if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
            db_url = "sqlite:////tmp/khayal.db"
        else:
            db_url = "sqlite:///khayal.db"
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.modules.auth.routes import auth_bp
    from app.modules.feed.routes import feed_bp
    from app.modules.posts.routes import posts_bp
    from app.modules.search.routes import search_bp
    from app.modules.profiles.routes import profiles_bp
    from app.modules.settings.routes import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        try:
            db.create_all()
            _seed_demo()
        except Exception as e:
            print(f"[WARN] DB init: {e}")

    return app


def _seed_demo():
    from app.models import User, Post
    from app.extensions import db
    if User.query.count() > 0:
        return
    u = User(username="khayal", email="hello@khayal.app", display_name="خيال")
    u.set_password("demo1234")
    u.bio = "الحساب الرسمي"
    db.session.add(u)
    db.session.flush()
    db.session.add(Post(author_id=u.id, body="اكتب مقالا عن [الموضوع]", category="writing", is_public=True))
    db.session.add(Post(author_id=u.id, body="Cinematic still, [وصف], 8k", category="image", is_public=True))
    db.session.add(Post(author_id=u.id, body="راجع كود بايثون وحسّنه", category="code", is_public=True))
    db.session.commit()