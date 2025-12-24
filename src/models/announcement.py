from src.db import db

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.BigInteger, nullable=False)
    target_audience = db.Column(db.Enum('all', 'teachers', 'students', 'specific_section'), default='all')
    section_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=True)
    admin_id = db.Column(db.BigInteger, db.ForeignKey("admin.id"), nullable=True)

    teacher = db.relationship('Teacher', backref='teacher_announcements', lazy=True)
    admin = db.relationship('Admin', backref='admin_announcements', lazy=True)