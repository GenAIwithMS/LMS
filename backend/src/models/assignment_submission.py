from src.db import db, pakistan_time

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submission'
    # One submission per student and assignment (a resubmission replaces it)
    __table_args__ = (db.UniqueConstraint('student_id', 'assignment_id', name='uq_submission_student_assignment'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column(db.BigInteger,db.ForeignKey('students.id'), nullable=False)
    assignment_id = db.Column(db.BigInteger, db.ForeignKey('assignments.id'), nullable=False)
    submission_text = db.Column(db.Text, nullable=True)
    submission_file = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=pakistan_time)
    marks = db.Column(db.Numeric(5, 2), nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    student = db.relationship('Student', backref='submissions', lazy=True)
    assignment = db.relationship('Assignment', backref='submissions', lazy=True)