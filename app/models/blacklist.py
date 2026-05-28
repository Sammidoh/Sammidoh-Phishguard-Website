from app.extensions import db
from datetime import datetime

class BlacklistedURL(db.Model):
    __tablename__ = 'blacklisted_urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('threat_categories.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by = db.Column(db.String(100))
    risk_score = db.Column(db.Integer, default=100)
    notes = db.Column(db.Text)

    category = db.relationship('ThreatCategory', backref='urls')
