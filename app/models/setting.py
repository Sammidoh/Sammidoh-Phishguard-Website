from app.extensions import db

class UserSettings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    protection_enabled = db.Column(db.Boolean, default=True)
    strict_mode = db.Column(db.Boolean, default=False)
    warning_sensitivity = db.Column(db.String(20), default='medium')
    dark_mode = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('settings', uselist=False))
