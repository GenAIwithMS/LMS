from src.db import db
from datetime import datetime
from zoneinfo import ZoneInfo

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.now(ZoneInfo("Asia/Karachi")))
    status = db.Column(db.Enum('active', 'completed', 'dropped'), default='active')
    grade = db.Column(db.String(2), nullable=True)

    student = db.relationship('Student', backref='enrollments', lazy=True)
    course = db.relationship('Course', backref='enrollments', lazy=True)

