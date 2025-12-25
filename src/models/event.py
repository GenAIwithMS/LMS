from src.db import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    admin_id = db.Column(db.BigInteger,db.ForeignKey("admin.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    admin = db.relationship('Admin', backref='admin_events', lazy=True)