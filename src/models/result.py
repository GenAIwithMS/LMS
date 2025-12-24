from src.db import db

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger,db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), nullable=False)
    obtained_marks = db.Column(db.Numeric(5, 2), nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    exam_type = db.Column(db.Enum('midterm', 'final', 'quiz', 'assignment'), default='final')
    remarks = db.Column(db.Text, nullable=True)

    student = db.relationship('Student', backref='student_results', lazy=True)
    subject = db.relationship('Subject', backref='subject_results', lazy=True)
