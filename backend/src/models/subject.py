from src.db import db

class Subject(db.Model):
    """A subject in a class's syllabus, like Maths for Class 5.

    Who teaches it is set per section (TeachingAssignment). teacher_id and
    course_id are from the old course system and are empty for new subjects.
    """
    __tablename__ = 'subjects'
    __table_args__ = (db.UniqueConstraint('class_id', 'name', name='uq_subject_class_name'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    class_id = db.Column(db.BigInteger, db.ForeignKey("school_classes.id"), nullable=True)
    teacher_id = db.Column(db.BigInteger,db.ForeignKey("teachers.id"), nullable=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey("courses.id"), nullable=True)

    teacher = db.relationship('Teacher', backref='subjects', lazy=True, foreign_keys=[teacher_id])
    course = db.relationship('Course', backref='subjects', lazy=True)
    school_class = db.relationship('SchoolClass', backref='subjects', lazy=True)
