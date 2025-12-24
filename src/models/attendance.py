from src.db import db

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    time = db.Column(db.Time, nullable=False)
    student_id = db.Column(db.BigInteger,db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='present')

    student = db.relationship('Student', backref='student_attendances', lazy=True)
    subject = db.relationship('Subject', backref='subject_attendances', lazy=True)
