from src.db import db, pakistan_time

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)

    teacher = db.relationship('Teacher', backref='courses', lazy=True)