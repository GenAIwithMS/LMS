from src.db import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    teacher = db.relationship('Teacher', backref='teacher_courses', lazy=True)
    # student = db.relationship('Student', secondary='enrollment', backref='courses', lazy=True)