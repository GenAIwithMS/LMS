from src.db import db

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'completed', 'dropped'), default='active')
    grade = db.Column(db.String(2), nullable=True)

