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
    """One chapter of a subject's syllabus in one section, e.g. 5-A Maths, chapter 3 "Fractions".

    Each section has its own syllabus, written by the teacher who teaches the subject there
    (5-A and 5-B Maths can differ). Chapters from before this change may have no section.
    """
    __tablename__ = 'syllabus_chapters'
    __table_args__ = (db.UniqueConstraint('subject_id', 'section_id', 'number', name='uq_chapter_subject_section_number'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=True)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    subject = db.relationship('Subject', backref='chapters', lazy=True)
    section = db.relationship('Section', lazy=True)
    topics = db.relationship('SyllabusTopic', backref='chapter', lazy=True, order_by='SyllabusTopic.number')


class SyllabusTopic(db.Model):
    """One daily topic of a chapter, e.g. "Adding fractions with the same denominator".

    The teacher plans the day for it and ticks it off when it has been taught. Assignments,
    class tests and diary entries made from a done topic point back to it.
    """
    __tablename__ = 'syllabus_topics'
    __table_args__ = (db.UniqueConstraint('chapter_id', 'number', name='uq_topic_chapter_number'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_chapters.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    planned_date = db.Column(db.Date, nullable=True)    # the day the teacher plans to teach it
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    done_on = db.Column(db.Date, nullable=True)


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


class TeacherSubject(db.Model):
    """A subject a teacher can teach, like "Urdu", before (or without) any class.

    Stored by subject name, because "Urdu" is a subject of many classes. The admin
    adds these right after adding a teacher; sections come later.
    """
    __tablename__ = 'teacher_subjects'
    __table_args__ = (db.UniqueConstraint('teacher_id', 'subject_name', name='uq_teacher_subject_name'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)

    teacher = db.relationship('Teacher', backref='subject_skills', lazy=True)
