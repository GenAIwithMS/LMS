from src.db import db
from datetime import datetime
from zoneinfo import ZoneInfo


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)
    target_audience = db.Column(db.String(50), default='all')
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(ZoneInfo("Asia/Karachi")))

    section = db.relationship("Section", backref="announcements",lazy=True)
    teacher = db.relationship("Teacher", backref="announcements",lazy=True)