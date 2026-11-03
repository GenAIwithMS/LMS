from src.db import db, pakistan_time

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    # A student can be enrolled in the same course only once
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='uq_enrollment_student_course'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=pakistan_time)
    status = db.Column(db.Enum('active', 'completed', 'dropped'), default='active')
    grade = db.Column(db.String(2), nullable=True)

    student = db.relationship('Student', backref='enrollments', lazy=True)
    course = db.relationship('Course', backref='enrollments', lazy=True)

