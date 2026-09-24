def _seed_demo():
    from app.models import User, Post
    from app.extensions import db

    if User.query.count() > 0:
        return
    u = User(username="khayal", email="hello@khayal.app", display_name="خيال")
    u.set_password("demo1234")
    u.bio = "الحساب الرسمي — مكتبة ومنصة البرومبتات العربية"
    db.session.add(u)
    db.session.flush()
    samples = [
        ("أنت كاتب محتوى عربي محترف. اكتب مقالاً عن [الموضوع] بأسلوب سلس مع عناوين فرعية.", "writing"),
        ("Cinematic still, [وصف], dramatic lighting, 8k, film grain --ar 16:9", "image"),
        ("راجع كود بايثون التالي واقترح تحسينات مع تعليقات بالعربية:\n\n```python\n# الكود\n```", "code"),
    ]
    for body, cat in samples:
        db.session.add(
            Post(author_id=u.id, body=body, category=cat, is_public=True)
        )
    db.session.commit()
    print("[seed] demo user: khayal / demo1234")