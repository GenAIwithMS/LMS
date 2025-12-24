from src.db import db

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    student_id = db.Column(db.BigInteger,db.ForeignKey('students.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), default=100.00)

    subject = db.relationship('Subject', backref='subject_assignments', lazy=True)
    student = db.relationship('Student', backref='student_assignments', lazy=True)