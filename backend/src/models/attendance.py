from src.db import db
from datetime import datetime
from zoneinfo import ZoneInfo

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    mark_at = db.Column(db.DateTime, default=datetime.now(ZoneInfo("Asia/Karachi")))
    student_id = db.Column(db.BigInteger,db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='present')

    student = db.relationship('Student', backref='attendances', lazy=True)
    subject = db.relationship('Subject', backref='attendances', lazy=True)
