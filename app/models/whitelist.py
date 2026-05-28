from app.extensions import db
from datetime import datetime

class WhitelistedURL(db.Model):
    __tablename__ = 'whitelist_urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(200))
