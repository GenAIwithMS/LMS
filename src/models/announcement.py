from src.db import db

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # posted_by_role = db.Column(db.Enum("admin","teacher"), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)
    # target_audience = db.Column(db.Enum('all', 'teachers', 'students', 'specific_section'), default='all')
    target_audience = db.Column(db.String(50), default='all')
    # section_name = db.Column(db.String(255), nullable=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    section = db.relationship("Section", backref="announcements",lazy=True)
    teacher = db.relationship("Teacher", backref="teacher_announcements",lazy=True)