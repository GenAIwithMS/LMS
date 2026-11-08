from src.db import db, pakistan_time

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    # The section the assignment is for. Empty for assignments from before the school system.
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=True)
    topic_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_topics.id'), nullable=True)   # the topic it was set on
    teacher_id = db.Column(db.BigInteger,db.ForeignKey('teachers.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), default=100.00)
    created_at = db.Column(db.DateTime, default=pakistan_time)

    subject = db.relationship('Subject', backref='assignments', lazy=True)
    teacher = db.relationship('Teacher', backref='assignments', lazy=True)
    section = db.relationship('Section', lazy=True)
    topic = db.relationship('SyllabusTopic', lazy=True)
