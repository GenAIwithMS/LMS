from src.db import db, pakistan_time


class DailyAttendance(db.Model):
    """One student's attendance for one school day, marked by the section's class incharge.

    status is one of: present, absent, late, leave.
    """
    __tablename__ = 'daily_attendance'
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='uq_daily_attendance_student_date'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='present')
    marked_by = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)
    marked_at = db.Column(db.DateTime, default=pakistan_time)

    student = db.relationship('Student', backref='daily_attendance', lazy=True)
    section = db.relationship('Section', backref='daily_attendance', lazy=True)
    teacher = db.relationship('Teacher', lazy=True)


class ChapterProgress(db.Model):
    """How far a section has got with one chapter, e.g. 5-A Maths chapter 3 is "done".

    status is one of: not_started, in_progress, done.
    """
    __tablename__ = 'chapter_progress'
    __table_args__ = (db.UniqueConstraint('section_id', 'chapter_id', name='uq_progress_section_chapter'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    chapter_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_chapters.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='not_started')
    planned_date = db.Column(db.Date, nullable=True)     # when the teacher plans to finish it
    started_on = db.Column(db.Date, nullable=True)
    completed_on = db.Column(db.Date, nullable=True)
    updated_by = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=pakistan_time, onupdate=pakistan_time)

    section = db.relationship('Section', lazy=True)
    chapter = db.relationship('SyllabusChapter', lazy=True)


class DiaryEntry(db.Model):
    """The daily diary: what was taught in a subject today (classwork) and the homework given."""
    __tablename__ = 'diary_entries'
    __table_args__ = (db.UniqueConstraint('section_id', 'subject_id', 'date', name='uq_diary_section_subject_date'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    classwork = db.Column(db.Text, nullable=True)
    homework = db.Column(db.Text, nullable=True)
    topic_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_topics.id'), nullable=True)   # the topic it was written from
    created_at = db.Column(db.DateTime, default=pakistan_time)

    section = db.relationship('Section', lazy=True)
    subject = db.relationship('Subject', lazy=True)
    teacher = db.relationship('Teacher', lazy=True)
    topic = db.relationship('SyllabusTopic', lazy=True)


class ClassTest(db.Model):
    """A short test a subject teacher takes in one section, e.g. a Maths quiz in 5-A."""
    __tablename__ = 'class_tests'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=False)
    chapter_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_chapters.id'), nullable=True)
    topic_id = db.Column(db.BigInteger, db.ForeignKey('syllabus_topics.id'), nullable=True)   # the topic it tests
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)

    section = db.relationship('Section', lazy=True)
    subject = db.relationship('Subject', lazy=True)
    teacher = db.relationship('Teacher', lazy=True)
    chapter = db.relationship('SyllabusChapter', lazy=True)
    topic = db.relationship('SyllabusTopic', lazy=True)


class ClassTestMark(db.Model):
    """One student's marks in a class test. obtained_marks is empty when the student was absent."""
    __tablename__ = 'class_test_marks'
    __table_args__ = (db.UniqueConstraint('test_id', 'student_id', name='uq_test_mark_test_student'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    test_id = db.Column(db.BigInteger, db.ForeignKey('class_tests.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    obtained_marks = db.Column(db.Numeric(5, 2), nullable=True)

    test = db.relationship('ClassTest', backref='marks', lazy=True)
    student = db.relationship('Student', lazy=True)


class TimetablePeriod(db.Model):
    """One period of a section's weekly timetable, e.g. 5-A, Monday, period 2: Maths.

    day is 1 (Monday) to 6 (Saturday). The teacher is whoever teaches that subject
    in that section, so changing the subject teacher updates the timetable too.
    """
    __tablename__ = 'timetable_periods'
    __table_args__ = (db.UniqueConstraint('section_id', 'day', 'period', name='uq_timetable_section_day_period'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)

    section = db.relationship('Section', lazy=True)
    subject = db.relationship('Subject', lazy=True)
