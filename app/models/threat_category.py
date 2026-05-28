from app.extensions import db

class ThreatCategory(db.Model):
    __tablename__ = 'threat_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
