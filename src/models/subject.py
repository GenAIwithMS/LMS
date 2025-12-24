from src.db import db

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    teacher_id = db.Column(db.BigInteger,db.ForeignKey("teachers.id"), nullable=False)
    course_code = db.Column(db.String(50), nullable=True)

    teacher = db.relationship('Teacher', backref='subjects', lazy=True)