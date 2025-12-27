from src.db import db

class StudentTeacher(db.Model):
    __tablename__ = 'student_teacher'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.BigInteger,db.ForeignKey("teachers.id"), nullable=False)

    student = db.relationship('Student', backref='teachers', lazy=True)
    teacher = db.relationship('Teacher', backref='students', lazy=True)
