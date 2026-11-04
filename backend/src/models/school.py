from src.db import db, pakistan_time


class AcademicSession(db.Model):
    """A school year, like "2026-27". One session is marked as the current one."""
    __tablename__ = 'academic_sessions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)


class SchoolClass(db.Model):
    """One of Class 1 to Class 10. Created automatically; level is 1 to 10."""
    __tablename__ = 'school_classes'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    level = db.Column(db.Integer, nullable=False, unique=True)


class SyllabusChapter(db.Model):
    """One chapter of a subject's syllabus, e.g. Class 5 Maths, chapter 3 "Fractions"."""
    __tablename__ = 'syllabus_chapters'
    __table_args__ = (db.UniqueConstraint('subject_id', 'number', name='uq_chapter_subject_number'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    subject = db.relationship('Subject', backref='chapters', lazy=True)


class TeachingAssignment(db.Model):
    """Who teaches a subject in a section, e.g. Maths in 5-A is taught by Ms Sara.

    Each subject of a section has at most one teacher.
    """
    __tablename__ = 'teaching_assignments'
    __table_args__ = (db.UniqueConstraint('section_id', 'subject_id', name='uq_teaching_section_subject'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)

    section = db.relationship('Section', backref='teaching_assignments', lazy=True)
    subject = db.relationship('Subject', backref='teaching_assignments', lazy=True)
    teacher = db.relationship('Teacher', backref='teaching_assignments', lazy=True)
