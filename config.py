import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "change-me-in-production-please-use-long-random"
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    _db = (os.getenv("DATABASE_URL") or "").strip()
    if not _db:
        # Vercel serverless: فقط /tmp قابل للكتابة
        if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
            _db = "sqlite:////tmp/khayal.db"
        else:
            _db = "sqlite:///khayal.db"

    # Heroku / some hosts use postgres:// — SQLAlchemy 2 needs postgresql://
    if _db.startswith("postgres://"):
        _db = _db.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Safer for serverless / Postgres
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30
