from datetime import datetime
from app.extensions import db


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), default="")
    category = db.Column(db.String(50), default="general", index=True)
    is_public = db.Column(db.Boolean, default=True)
    copy_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    save_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author = db.relationship("User", back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict() if self.author else None,
            "body": self.body,
            "image_url": self.image_url or "",
            "category": self.category,
            "is_public": self.is_public,
            "copy_count": self.copy_count or 0,
            "like_count": self.like_count or 0,
            "save_count": self.save_count or 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }