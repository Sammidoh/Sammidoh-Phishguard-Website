from app.extensions import db
from datetime import datetime

class BlockedLog(db.Model):
    __tablename__ = 'blocked_logs'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    threat_category = db.Column(db.String(50))
    user_action = db.Column(db.String(20), default='blocked')
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    risk_score = db.Column(db.Integer)
