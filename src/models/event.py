from src.db import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    event_type = db.Column(db.Enum('class', 'exam', 'holiday', 'meeting', 'assignment_due'), nullable=False)
    related_to_id = db.Column(db.BigInteger, nullable=True)
    created_by = db.Column(db.BigInteger, nullable=False)
    created_by_type = db.Column(db.Enum('admin', 'teacher'), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=True)
    admin_id = db.Column(db.BigInteger,db.ForeignKey("admin.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    teacher = db.relationship('Teacher', backref='teacher_events', lazy=True)
    admin = db.relationship('Admin', backref='admin_events', lazy=True)